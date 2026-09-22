import os
import sys
sys.path.insert(0, os.path.abspath("."))
from bs4 import BeautifulSoup
from app import app, db, User, HealthRecord

def test_measurement_contexts():
    print("=" * 80)
    print("TESTING DAILY CHECK-IN MEASUREMENT CONTEXT SELECTION & PERSISTENCE")
    print("=" * 80)

    client = app.test_client()

    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        if not user:
            print("Creating test user Rahul Kumar")
            user = User(
                name="Rahul Kumar",
                email="rahul.test2026@example.com",
                password="secure_password",
                age=42,
                profile_completed=True,
                onboarding_completed=True
            )
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)

        user_id = user.id

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # 1. Test GET /monitoring page rendering
    resp = client.get("/monitoring")
    assert resp.status_code == 200, f"GET /monitoring returned {resp.status_code}"
    soup = BeautifulSoup(resp.data.decode("utf-8"), "html.parser")

    radio_cards = soup.find_all(class_="radio-card")
    assert len(radio_cards) == 6, f"Expected 6 radio cards, found {len(radio_cards)}"
    
    expected_contexts = [
        "Fasting",
        "Pre-meal",
        "Post-meal (1h)",
        "Post-meal (2h)",
        "Bedtime",
        "Random"
    ]

    card_contexts = [c.get("data-context") for c in radio_cards]
    assert card_contexts == expected_contexts, f"Mismatch in card contexts: {card_contexts}"
    print(f"[PASS] All 6 measurement context cards rendered properly: {card_contexts}")

    # Check hidden input
    hidden_input = soup.find("input", {"id": "meal_context_input"})
    assert hidden_input is not None, "Missing hidden input #meal_context_input"
    print(f"[PASS] Hidden input #meal_context_input present with default value '{hidden_input.get('value')}'")

    # 2. Test submitting ALL SIX options individually
    created_records = []
    
    for context in expected_contexts:
        payload = {
            "glucose": "130.0",
            "meal_context": context,
            "stress": "4",
            "sleep": "7.5",
            "steps": "6500",
            "weight": "72.0",
            "exercise_duration": "30",
            "mood": "7"
        }
        
        post_resp = client.post("/add_record", data=payload, follow_redirects=False)
        assert post_resp.status_code == 302, f"Expected redirect after check-in, got {post_resp.status_code}"
        
        with app.app_context():
            rec = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.id.desc()).first()
            assert rec is not None, "Record not found in database"
            assert rec.meal_context == context, f"Expected meal_context='{context}', got '{rec.meal_context}'"
            assert rec.glucose == 130.0, f"Expected glucose=130.0, got {rec.glucose}"
            created_records.append(rec.id)
            print(f"[PASS] Context '{context:<15}': Successfully sent via POST, saved to DB (Record ID: {rec.id}), retrieved value='{rec.meal_context}'")

    # 3. Test Invalid Context Validation
    invalid_payload = {
        "glucose": "130.0",
        "meal_context": "InvalidContext123",
        "stress": "4",
        "sleep": "7.5",
        "steps": "6500",
        "weight": "72.0",
        "exercise_duration": "30"
    }
    inv_resp = client.post("/add_record", data=invalid_payload, follow_redirects=True)
    assert "Please select a valid Measurement context" in inv_resp.data.decode("utf-8"), "Missing validation error for invalid context"
    print("[PASS] Invalid context rejected with validation message.")

    # 4. Clean up test records
    with app.app_context():
        for r_id in created_records:
            r = HealthRecord.query.get(r_id)
            if r:
                db.session.delete(r)
        db.session.commit()
    print("[PASS] Test health records safely cleaned up.")

    print("\n" + "=" * 80)
    print("ALL 6 MEASUREMENT CONTEXT OPTIONS VERIFIED: UI, POST, PERSISTENCE & RETRIEVAL")
    print("=" * 80)

if __name__ == "__main__":
    test_measurement_contexts()
