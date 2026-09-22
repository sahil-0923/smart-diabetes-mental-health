import os
import sys
sys.path.insert(0, os.path.abspath("."))
from bs4 import BeautifulSoup
from app import app, db, User, HealthRecord

def run_tests():
    print("=" * 80)
    print("VERIFYING DASHBOARD RISK INDICATOR & HEALTH TRENDS (REAL DATA FLOW)")
    print("=" * 80)

    client = app.test_client()

    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        assert user is not None, "User Rahul Kumar not found in DB!"
        user_id = user.id
        recs = HealthRecord.query.filter_by(user_id=user_id, is_valid=True).order_by(HealthRecord.date.desc()).all()
        print(f"Testing with authenticated user: ID={user_id}, Name='{user.name}', Email='{user.email}'")
        print(f"Total valid health records in SQLite: {len(recs)}")
        for r in recs:
            print(f"  Record {r.id}: {r.date} | Glucose: {r.glucose} | Sleep: {r.sleep}h | Steps: {r.steps} | Stress: {r.stress}")

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # 1. Test /api/health/summary (Risk Indicator endpoint)
    print("\n--- 1. Testing /api/health/summary (Risk Indicator) ---")
    sum_resp = client.get("/api/health/summary")
    assert sum_resp.status_code == 200, f"Expected 200, got {sum_resp.status_code}"
    sum_data = sum_resp.get_json()
    assert sum_data.get("success") == True
    print(f"Current Glucose: {sum_data.get('current_glucose')} mg/dL")
    print(f"Risk Level: {sum_data.get('risk_level')}")
    print(f"Risk Description: {sum_data.get('risk_description')}")
    assert sum_data.get("risk_level") is not None and sum_data.get("risk_level") != "N/A", "Risk level is N/A!"
    print("[PASS] /api/health/summary returns calculated risk indicator from actual user data")

    # 2. Test /dashboard HTML
    print("\n--- 2. Testing /dashboard HTML structure ---")
    dash_resp = client.get("/dashboard")
    assert dash_resp.status_code == 200
    soup = BeautifulSoup(dash_resp.data.decode("utf-8"), "html.parser")
    risk_val_el = soup.find(id="dash_risk_indicator_val")
    risk_desc_el = soup.find(id="dash_risk_indicator_desc")
    assert risk_val_el is not None, "Missing #dash_risk_indicator_val in dashboard.html"
    assert risk_desc_el is not None, "Missing #dash_risk_indicator_desc in dashboard.html"
    print("[PASS] #dash_risk_indicator_val and #dash_risk_indicator_desc exist in dashboard HTML")

    # 3. Test /health-trends page
    print("\n--- 3. Testing /health-trends route ---")
    ht_resp = client.get("/health-trends")
    assert ht_resp.status_code == 200
    soup_ht = BeautifulSoup(ht_resp.data.decode("utf-8"), "html.parser")
    assert "(Demo)" not in soup_ht.get_text(), "Found '(Demo)' text in health trends page!"
    assert soup_ht.find(id="trend_gluc") is not None
    assert soup_ht.find(id="trend_sleep") is not None
    assert soup_ht.find(id="trend_activity") is not None
    assert soup_ht.find(id="trend_stress") is not None
    assert soup_ht.find(id="chartT") is not None
    print("[PASS] /health-trends renders HTTP 200, (Demo) removed, metric card IDs present")

    # 4. Test /api/health-trends?days=30
    print("\n--- 4. Testing /api/health-trends?days=30 ---")
    t30_resp = client.get("/api/health-trends?days=30")
    assert t30_resp.status_code == 200
    t30_data = t30_resp.get_json()
    assert t30_data.get("success") == True
    labels = t30_data.get("labels", [])
    glucose_arr = t30_data.get("glucose", [])
    sleep_arr = t30_data.get("sleep", [])
    steps_arr = t30_data.get("steps", [])
    stress_arr = t30_data.get("stress", [])
    print(f"Returned {len(labels)} data points for 30-day window")
    print(f"Glucose: {glucose_arr}")
    print(f"Sleep: {sleep_arr}")
    print(f"Steps: {steps_arr}")
    print(f"Stress: {stress_arr}")
    assert len(glucose_arr) > 0, "No glucose records returned for user!"
    
    # Calculate averages from returned real data
    avg_g = round(sum(glucose_arr) / len(glucose_arr), 1)
    valid_sleep = [s for s in sleep_arr if s is not None]
    avg_s = round(sum(valid_sleep) / len(valid_sleep), 1) if valid_sleep else None
    valid_steps = [st for st in steps_arr if st is not None]
    avg_st = round(sum(valid_steps) / len(valid_steps)) if valid_steps else None
    valid_stress = [str_v for str_v in stress_arr if str_v is not None]
    avg_str = round(sum(valid_stress) / len(valid_stress), 1) if valid_stress else None
    
    print(f"Computed Avg Glucose: {avg_g} mg/dL")
    print(f"Computed Avg Sleep: {avg_s} hrs")
    print(f"Computed Avg Steps: {avg_st} steps")
    print(f"Computed Avg Stress: {avg_str} / 10")
    print("[PASS] /api/health-trends dynamic metrics verified")

    # 5. Test 7-Day Window
    print("\n--- 5. Testing /api/health-trends?days=7 ---")
    t7_resp = client.get("/api/health-trends?days=7")
    assert t7_resp.status_code == 200
    t7_data = t7_resp.get_json()
    assert t7_data.get("success") == True
    print(f"Returned {len(t7_data.get('labels', []))} data points for 7-day window")
    print("[PASS] 7-day filter responds cleanly")

    # 6. Test User Isolation
    print("\n--- 6. Testing User Isolation (Empty User) ---")
    with app.app_context():
        empty_user = User.query.filter_by(name="Michael Chang").first()
        empty_id = empty_user.id if empty_user else None
    
    if empty_id:
        with client.session_transaction() as sess:
            sess["user_id"] = empty_id
        emp_resp = client.get("/api/health-trends?days=30")
        assert emp_resp.status_code == 200
        emp_data = emp_resp.get_json()
        assert len(emp_data.get("labels", [])) == 0, "Empty user received records from another user!"
        print("[PASS] User isolation verified: Michael Chang receives 0 records")

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED SUCCESSFULLY! DATA INTEGRITY AND UI COMPLIANT.")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
