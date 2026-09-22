import os
import sys
sys.path.insert(0, os.path.abspath("."))
from bs4 import BeautifulSoup
from app import app, db, User, HealthRecord

def test_full_user_flow():
    print("=" * 80)
    print("TESTING CONTROLLED CHECK-IN SUBMISSION & DASHBOARD RECENT RECORDS")
    print("=" * 80)

    client = app.test_client()

    with app.app_context():
        # Find active user Rahul Kumar
        user = User.query.filter_by(name="Rahul Kumar").first()
        assert user is not None, "Active user Rahul Kumar not found in database!"
        user_id = user.id
        print(f"Logged in as User ID: {user_id}, Name: '{user.name}', Email: '{user.email}'")

        # Check existing records before test
        prior_recs = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.date.desc()).all()
        print(f"Prior records count: {len(prior_recs)}")
        for r in prior_recs:
            print(f"  Prior record {r.id}: {r.date} | {r.glucose} mg/dL | Context: '{r.meal_context}'")

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # Step 1: Submit new controlled check-in: glucose = 122, context = Pre-meal
    payload = {
        "glucose": "122",
        "meal_context": "Pre-meal",
        "stress": "3",
        "sleep": "8.0",
        "steps": "7200",
        "weight": "71.5",
        "exercise_duration": "35",
        "mood": "8"
    }
    
    post_resp = client.post("/add_record", data=payload, follow_redirects=False)
    assert post_resp.status_code == 302, f"Expected 302 redirect, got {post_resp.status_code}"
    print("\n[PASS] Submitted Daily Check-in with glucose=122, meal_context='Pre-meal'")

    # Step 2: Verify Database persistence
    with app.app_context():
        latest = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.id.desc()).first()
        assert latest is not None, "No record found in database after submission!"
        assert latest.glucose == 122.0, f"Expected glucose=122.0, got {latest.glucose}"
        assert latest.meal_context == "Pre-meal", f"Expected meal_context='Pre-meal', got '{latest.meal_context}'"
        print(f"[PASS] Database verified: Record ID={latest.id}, Date={latest.date}, Glucose={latest.glucose} mg/dL, Context='{latest.meal_context}'")

    # Step 3: Verify /api/health-records/recent endpoint
    api_resp = client.get("/api/health-records/recent?limit=5")
    assert api_resp.status_code == 200, f"Expected 200, got {api_resp.status_code}"
    data = api_resp.get_json()
    assert data.get("success") == True, "API returned success=False"
    records = data.get("records", [])
    assert len(records) > 0, "API returned empty records list"
    top_record = records[0]
    
    assert top_record["glucose"] == 122.0, f"Expected top record glucose=122.0, got {top_record['glucose']}"
    assert top_record["meal_context"] == "Pre-meal", f"Expected top record context='Pre-meal', got '{top_record['meal_context']}'"
    print(f"[PASS] /api/health-records/recent verified: Top record is {top_record['glucose']} mg/dL with context '{top_record['meal_context']}' and timestamp '{top_record['timestamp']}'")

    # Step 4: Verify Dashboard Page HTML & View All Link
    dash_resp = client.get("/dashboard")
    assert dash_resp.status_code == 200
    soup = BeautifulSoup(dash_resp.data.decode("utf-8"), "html.parser")
    
    view_all_link = soup.find("a", string=lambda s: s and "View all" in s)
    assert view_all_link is not None, "Missing 'View all' link in dashboard"
    assert view_all_link.get("href") == "/glucose", f"Expected href='/glucose', got '{view_all_link.get('href')}'"
    print(f"[PASS] Dashboard 'View all ->' link correctly points to '{view_all_link.get('href')}'")

    # Step 5: Verify Glucose History Page
    gluc_resp = client.get("/glucose")
    assert gluc_resp.status_code == 200
    print("[PASS] Glucose Monitor (/glucose) history page renders with HTTP 200")

    print("\n" + "=" * 80)
    print("ALL VERIFICATION CHECKS PASSED: DATA INTEGRITY & VIEW ALL FULLY FUNCTIONAL")
    print("=" * 80)

if __name__ == "__main__":
    test_full_user_flow()
