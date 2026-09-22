import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import sqlite3
from datetime import datetime, timedelta

from app import app, db, User, HealthRecord

def run_rahul_audit():
    print("=" * 80)
    print("COMPREHENSIVE FINAL AUDIT & PIPELINE VERIFICATION")
    print("=" * 80)

    with app.app_context():
        # Setup Test User: Rahul Kumar
        email = "rahul.kumar@diabetesai.org"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name="Rahul Kumar",
                email=email,
                password="hashed_secure_password",
                age=42,
                gender="Male",
                height=175.0,
                weight=76.0,
                diabetes_type="Type 2",
                years_since_diagnosis=5,
                hba1c=7.1,
                blood_pressure="125/82",
                cholesterol=4.5,
                profile_completed=True,
                onboarding_completed=True
            )
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
        else:
            user.name = "Rahul Kumar"
            user.profile_completed = True
            user.onboarding_completed = True
            db.session.commit()

        user_id = user.id

        # Clean existing records for this user
        HealthRecord.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        # Insert exact 5 known readings
        base_time = datetime.utcnow()
        known_readings = [
            {"date": base_time - timedelta(days=4), "glucose": 125.0, "stress": 4.0, "sleep": 7.0, "steps": 6200, "exercise": 30.0, "meal": "Fasting"},
            {"date": base_time - timedelta(days=3), "glucose": 130.0, "stress": 5.0, "sleep": 6.5, "steps": 5400, "exercise": 20.0, "meal": "Before Meal"},
            {"date": base_time - timedelta(days=2), "glucose": 122.0, "stress": 3.0, "sleep": 8.0, "steps": 7500, "exercise": 45.0, "meal": "After Meal"},
            {"date": base_time - timedelta(days=1), "glucose": 138.0, "stress": 6.0, "sleep": 6.0, "steps": 4800, "exercise": 15.0, "meal": "Random"},
            {"date": base_time - timedelta(hours=1), "glucose": 132.0, "stress": 4.0, "sleep": 7.5, "steps": 6800, "exercise": 30.0, "meal": "Fasting"}
        ]

        for kr in known_readings:
            hr = HealthRecord(
                user_id=user_id,
                date=kr["date"],
                glucose=kr["glucose"],
                stress=kr["stress"],
                sleep=kr["sleep"],
                steps=kr["steps"],
                exercise_duration=kr["exercise"],
                weight=76.0,
                mood="Good",
                meal_context=kr["meal"],
                is_valid=True,
                validation_notes="Valid"
            )
            db.session.add(hr)
        db.session.commit()

        # Query via ORM to verify
        records = HealthRecord.query.filter_by(user_id=user_id, is_valid=True).order_by(HealthRecord.date.asc()).all()
        print(f"\n1. DATABASE STATE FOR PATIENT: {user.name} (ID: {user_id})")
        print(f"  Age: {user.age} | Type: {user.diabetes_type} | Diagnosed: {user.years_since_diagnosis} yrs | HbA1c: {user.hba1c}%")
        print(f"  Valid Records in Database: {len(records)} rows")
        for r in records:
            print(f"    • ID: {r.id} | Date: {r.date} | Glucose: {r.glucose} mg/dL | Context: {r.meal_context} | Stress: {r.stress}/10 | Sleep: {r.sleep}h | Steps: {r.steps}")

        g_list = [r.glucose for r in records]
        py_latest = g_list[-1]
        py_prev = g_list[-2]
        py_delta = round(py_latest - py_prev, 1)
        py_avg = round(sum(g_list) / len(g_list), 1)
        py_max = max(g_list)
        py_min = min(g_list)

        print("\n2. INDEPENDENT PYTHON CALCULATIONS:")
        print(f"  • Latest Glucose:   {py_latest} mg/dL (Expected: 132.0)")
        print(f"  • Previous Glucose: {py_prev} mg/dL (Expected: 138.0)")
        print(f"  • Delta:            {py_delta} mg/dL (Expected: -6.0)")
        print(f"  • 7-Day Average:    {py_avg} mg/dL (Expected: 129.4)")
        print(f"  • Highest:          {py_max} mg/dL (Expected: 138.0)")
        print(f"  • Lowest:           {py_min} mg/dL (Expected: 122.0)")

        assert py_latest == 132.0
        assert py_prev == 138.0
        assert py_delta == -6.0
        assert py_avg == 129.4
        assert py_max == 138.0
        assert py_min == 122.0

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # 3A. Summary API
    resp_sum = client.get("/api/health/summary")
    sum_data = resp_sum.get_json()
    print("\n3. API RESPONSE: GET /api/health/summary")
    print(json.dumps(sum_data, indent=2))
    assert sum_data["current_glucose"] == 132.0
    assert sum_data["previous_glucose"] == 138.0
    assert sum_data["glucose_delta"] == -6.0
    assert sum_data["weekly_average_glucose"] == 129.4
    assert sum_data["highest_recent_glucose"] == 138.0
    assert sum_data["lowest_recent_glucose"] == 122.0

    # 3B. Glucose History API
    resp_gh = client.get("/api/glucose/history?days=7")
    gh_data = resp_gh.get_json()
    print("\n4. API RESPONSE: GET /api/glucose/history?days=7")
    print(f"  Labels: {gh_data['labels']}")
    print(f"  Values: {gh_data['values']}")
    print(f"  Stats:  {gh_data['stats']}")
    assert gh_data["values"] == [125.0, 130.0, 122.0, 138.0, 132.0]
    assert gh_data["stats"]["current"] == 132.0
    assert gh_data["stats"]["average"] == 129.4

    # 3C. Glucose Trend API
    resp_gt = client.get("/api/glucose/trend")
    gt_data = resp_gt.get_json()
    print("\n5. API RESPONSE: GET /api/glucose/trend")
    print(f"  Status: {gt_data['status']} | Trend: {gt_data['trend']} | Difference: {gt_data['difference']} mg/dL")

    # 3D. GRU Forecast API
    resp_fp = client.post("/api/forecast/predict")
    fp_data = resp_fp.get_json()
    print("\n6. API RESPONSE: POST /api/forecast/predict")
    print(json.dumps(fp_data, indent=2))
    assert fp_data["available"] is True
    assert fp_data["current_glucose"] == 132.0, f"Forecast current_glucose {fp_data['current_glucose']} != 132.0"
    
    pred_30 = fp_data["prediction_30min"]
    pred_60 = fp_data["prediction_60min"]
    print(f"\n  >>> LIVE RUNTIME GRU PREDICTIONS (Rahul Kumar):")
    print(f"      • Current Glucose: {fp_data['current_glucose']} mg/dL")
    print(f"      • 30-min Forecast: {pred_30} mg/dL")
    print(f"      • 60-min Forecast: {pred_60} mg/dL")

    # 3E. Simulator API
    resp_sim = client.post("/api/forecast/simulate", json={"meal_context": "Low Carb", "exercise_mins": 45, "sleep_hours": 8.0})
    sim_data = resp_sim.get_json()
    print("\n7. API RESPONSE: POST /api/forecast/simulate (Low Carb + 45m Exercise)")
    print(json.dumps(sim_data, indent=2))
    assert sim_data["available"] is True
    assert sim_data["baseline_30min"] == pred_30
    assert sim_data["baseline_60min"] == pred_60

    # 4. User Isolation Test
    print("\n8. TESTING USER ISOLATION (User B):")
    user_b_id = 99888
    with app.app_context():
        u_b = db.session.get(User, user_b_id)
        if not u_b:
            u_b = User(
                id=user_b_id,
                name="Michael Chang",
                email="michael.chang@diabetesai.org",
                password="hashed_secure_password",
                age=48,
                gender="Male",
                diabetes_type="Type 1",
                profile_completed=True,
                onboarding_completed=True
            )
            db.session.add(u_b)
            db.session.commit()
        HealthRecord.query.filter_by(user_id=user_b_id).delete()
        db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = user_b_id

    resp_sum_b = client.get("/api/health/summary")
    sum_b = resp_sum_b.get_json()
    resp_fp_b = client.post("/api/forecast/predict")
    fp_b = resp_fp_b.get_json()

    print(f"  User B /api/health/summary: {sum_b}")
    print(f"  User B /api/forecast/predict: {fp_b}")
    assert "current_glucose" not in sum_b or sum_b.get("current_glucose") is None
    assert fp_b["available"] is False
    assert fp_b["prediction_30min"] is None

    print("\n" + "=" * 80)
    print("ALL AUDIT AND CONSISTENCY TESTS PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    run_rahul_audit()
