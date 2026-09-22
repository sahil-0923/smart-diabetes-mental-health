import os
import json
import sqlite3
from datetime import datetime, timedelta
import numpy as np

from app import app, db, User, HealthRecord

def run_end_to_end_test():
    print("=" * 70)
    print("PHASE J — END-TO-END DATA PIPELINE VERIFICATION")
    print("=" * 70)

    client = app.test_client()

    with app.app_context():
        # Setup Test User A
        u_email = "audit_user_a@diabetesai.org"
        user_a = User.query.filter_by(email=u_email).first()
        if not user_a:
            user_a = User(
                name="Sarah Jenkins",
                email=u_email,
                password="hashed_secure_password",
                age=35,
                gender="Female",
                height=165.0,
                weight=63.0,
                diabetes_type="Type 2",
                years_since_diagnosis=4,
                hba1c=6.8,
                blood_pressure="120/80",
                cholesterol=4.2,
                profile_completed=True,
                onboarding_completed=True
            )
            db.session.add(user_a)
            db.session.commit()

        user_a_id = user_a.id
        HealthRecord.query.filter_by(user_id=user_a_id).delete()
        db.session.commit()

        # Insert 5 valid known records (Historical up to 2 hours ago)
        base_time = datetime.utcnow()
        known_readings = [
            {"date": base_time - timedelta(days=4), "glucose": 125.0, "stress": 3.0, "sleep": 7.5, "steps": 6000, "exercise": 30.0, "meal": "Fasting"},
            {"date": base_time - timedelta(days=3), "glucose": 130.0, "stress": 4.0, "sleep": 7.0, "steps": 5500, "exercise": 25.0, "meal": "Before Meal"},
            {"date": base_time - timedelta(days=2), "glucose": 122.0, "stress": 2.0, "sleep": 8.0, "steps": 7000, "exercise": 40.0, "meal": "After Meal"},
            {"date": base_time - timedelta(days=1), "glucose": 138.0, "stress": 5.0, "sleep": 6.5, "steps": 4500, "exercise": 20.0, "meal": "Random"},
            {"date": base_time - timedelta(hours=2), "glucose": 132.0, "stress": 3.0, "sleep": 7.5, "steps": 6200, "exercise": 30.0, "meal": "Fasting"}
        ]

        for kr in known_readings:
            hr = HealthRecord(
                user_id=user_a_id,
                date=kr["date"],
                glucose=kr["glucose"],
                stress=kr["stress"],
                sleep=kr["sleep"],
                steps=kr["steps"],
                exercise_duration=kr["exercise"],
                weight=63.0,
                mood="Good",
                meal_context=kr["meal"],
                is_valid=True,
                validation_notes="Valid"
            )
            db.session.add(hr)
        db.session.commit()

        # Direct SQLite Inspection
        conn = sqlite3.connect("smart_health.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE id = ?", (user_a_id,))
        db_user = dict(cur.fetchone())
        cur.execute("SELECT * FROM health_record WHERE user_id = ? AND is_valid = 1 ORDER BY date ASC", (user_a_id,))
        db_records = [dict(r) for r in cur.fetchall()]
        conn.close()

        print("\n1. DIRECT SQLITE DATABASE STATE (User A):")
        print(f"  User: ID={db_user['id']}, Name='{db_user['name']}', Age={db_user['age']}, DiabetesType='{db_user['diabetes_type']}', Diagnosed={db_user['years_since_diagnosis']} yrs, HbA1c={db_user['hba1c']}%")
        print(f"  Valid HealthRecords in DB: {len(db_records)} rows")
        for r in db_records:
            print(f"    - ID={r['id']} | Date={r['date']} | Glucose={r['glucose']} mg/dL | Meal={r['meal_context']} | Stress={r['stress']} | Sleep={r['sleep']}h | Steps={r['steps']}")

        # Independent Python Baseline Calculations
        g_vals = [r["glucose"] for r in db_records]
        s_vals = [r["stress"] for r in db_records]
        sl_vals = [r["sleep"] for r in db_records]
        py_latest_g = g_vals[-1]
        py_prev_g = g_vals[-2]
        py_delta_g = round(py_latest_g - py_prev_g, 1)
        py_avg_g = round(sum(g_vals) / len(g_vals), 1)
        py_highest_g = max(g_vals)
        py_lowest_g = min(g_vals)
        py_avg_stress = round(sum(s_vals) / len(s_vals), 1)
        py_avg_sleep = round(sum(sl_vals) / len(sl_vals), 1)

        print("\n2. INDEPENDENT PYTHON CALCULATIONS:")
        print(f"  Latest Glucose: {py_latest_g} mg/dL")
        print(f"  Previous Glucose: {py_prev_g} mg/dL")
        print(f"  Glucose Delta: {py_delta_g} mg/dL")
        print(f"  7-Day Average Glucose: {py_avg_g} mg/dL")
        print(f"  Highest Glucose: {py_highest_g} mg/dL")
        print(f"  Lowest Glucose: {py_lowest_g} mg/dL")
        print(f"  Stress Average: {py_avg_stress}/10")
        print(f"  Sleep Average: {py_avg_sleep} hours")

    # 3. Authenticated API Verification for User A
    with client.session_transaction() as sess:
        sess["user_id"] = user_a_id

    # 3A. Summary API
    resp_sum = client.get("/api/health/summary")
    sum_data = resp_sum.get_json()
    print("\n3. API RESPONSE: GET /api/health/summary:")
    print(f"  Status: {resp_sum.status_code}")
    print(f"  JSON: {json.dumps(sum_data, indent=2)}")

    assert sum_data["current_glucose"] == py_latest_g, f"Summary current glucose {sum_data['current_glucose']} != {py_latest_g}"
    assert sum_data["previous_glucose"] == py_prev_g, f"Summary previous glucose {sum_data['previous_glucose']} != {py_prev_g}"
    assert sum_data["glucose_delta"] == py_delta_g, f"Summary delta {sum_data['glucose_delta']} != {py_delta_g}"
    assert sum_data["weekly_average_glucose"] == py_avg_g, f"Summary average {sum_data['weekly_average_glucose']} != {py_avg_g}"
    assert sum_data["highest_recent_glucose"] == py_highest_g
    assert sum_data["lowest_recent_glucose"] == py_lowest_g
    assert sum_data["stress_average"] == py_avg_stress
    assert sum_data["sleep_average"] == py_avg_sleep

    # 3B. Glucose History API
    resp_gh = client.get("/api/glucose/history?days=7")
    gh_data = resp_gh.get_json()
    print("\n4. API RESPONSE: GET /api/glucose/history:")
    print(f"  Labels count: {len(gh_data['labels'])}")
    print(f"  Values: {gh_data['values']}")
    print(f"  Stats: {gh_data['stats']}")
    assert gh_data["values"] == g_vals, f"Chart values {gh_data['values']} != {g_vals}"

    # 3C. Glucose Trend API
    resp_gt = client.get("/api/glucose/trend")
    gt_data = resp_gt.get_json()
    print("\n5. API RESPONSE: GET /api/glucose/trend:")
    print(f"  Trend: {gt_data['status']} ({gt_data['description']})")

    # 3D. GRU Forecast API
    resp_fp = client.post("/api/forecast/predict")
    fp_data = resp_fp.get_json()
    print("\n6. API RESPONSE: POST /api/forecast/predict:")
    print(f"  JSON: {json.dumps(fp_data, indent=2)}")
    assert fp_data["available"] is True, "Forecast should be available with 5 valid readings"
    assert fp_data["prediction_30min"] is not None
    assert fp_data["prediction_60min"] is not None

    # 4. DAILY CHECK-IN ADDITION TEST
    print("\n7. TESTING DAILY CHECK-IN ADDITION (+1 RECORD):")
    with client.session_transaction() as sess:
        sess["user_id"] = user_a_id

    resp_add = client.post("/add_health", data={
        "glucose": "145.0",
        "stress": "4",
        "sleep": "7.0",
        "steps": "8000",
        "exercise_duration": "45",
        "weight": "63.0",
        "mood": "Good",
        "meal_context": "After Meal"
    }, follow_redirects=False)
    print(f"  POST /add_health HTTP Status: {resp_add.status_code}")

    # Re-verify summary
    resp_sum2 = client.get("/api/health/summary")
    sum_data2 = resp_sum2.get_json()
    print("\n8. API RESPONSE AFTER CHECK-IN: GET /api/health/summary:")
    print(f"  New Current Glucose: {sum_data2['current_glucose']} mg/dL (Expected: 145.0)")
    print(f"  New Previous Glucose: {sum_data2['previous_glucose']} mg/dL (Expected: 132.0)")
    print(f"  New Delta: {sum_data2['glucose_delta']} mg/dL (Expected: +13.0)")
    print(f"  New Average: {sum_data2['weekly_average_glucose']} mg/dL (Expected: 132.0)")

    assert sum_data2["current_glucose"] == 145.0
    assert sum_data2["previous_glucose"] == 132.0
    assert sum_data2["glucose_delta"] == 13.0
    assert sum_data2["weekly_average_glucose"] == 132.0

    # Re-verify forecast uses updated sequence
    resp_fp2 = client.post("/api/forecast/predict")
    fp_data2 = resp_fp2.get_json()
    print("\n9. API RESPONSE AFTER CHECK-IN: POST /api/forecast/predict:")
    print(f"  Input Records Count: {fp_data2['input_records']} (Expected: 6)")
    print(f"  Updated 30m Forecast: {fp_data2['prediction_30min']} mg/dL")
    print(f"  Updated 60m Forecast: {fp_data2['prediction_60min']} mg/dL")
    assert fp_data2["input_records"] == 6

    # 5. USER ISOLATION TEST (User B)
    print("\n10. TESTING USER ISOLATION (User B):")
    user_b_id = 99888
    with app.app_context():
        u_email_b = "audit_user_b@diabetesai.org"
        user_b = db.session.get(User, user_b_id)
        if not user_b:
            user_b = User(
                id=user_b_id,
                name="Michael Chang",
                email=u_email_b,
                password="hashed_secure_password",
                age=48,
                gender="Male",
                height=178.0,
                weight=82.0,
                diabetes_type="Type 1",
                years_since_diagnosis=10,
                hba1c=7.5,
                profile_completed=True,
                onboarding_completed=True
            )
            db.session.add(user_b)
            db.session.commit()
            
        HealthRecord.query.filter_by(user_id=user_b_id).delete()
        db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = user_b_id

    resp_sum_b = client.get("/api/health/summary")
    sum_data_b = resp_sum_b.get_json()
    print(f"  User B /api/health/summary: {sum_data_b}")
    assert "current_glucose" not in sum_data_b or sum_data_b.get("current_glucose") is None

    resp_fp_b = client.post("/api/forecast/predict")
    fp_data_b = resp_fp_b.get_json()
    print(f"  User B /api/forecast/predict: {fp_data_b}")
    assert fp_data_b["available"] is False
    assert fp_data_b["prediction_30min"] is None

    print("\n" + "=" * 70)
    print("ALL END-TO-END DATA FLOW TESTS PASSED COMPLETELY (100% REAL DATA)")
    print("=" * 70)

if __name__ == "__main__":
    run_end_to_end_test()
