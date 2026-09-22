import sqlite3

conn = sqlite3.connect("smart_health.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("ALL USERS IN DB:")
cur.execute("SELECT * FROM user ORDER BY id ASC")
users = cur.fetchall()
for u in users:
    print(f"ID={u['id']}, Name='{u['name']}', Email='{u['email']}', Age={u['age']}, Gender='{u['gender']}', Ht={u['height']}, Wt={u['weight']}, Type='{u['diabetes_type']}', Yrs={u['years_since_diagnosis']}, HbA1c={u['hba1c']}, BP='{u['blood_pressure']}', Chol={u['cholesterol']}, ProfileDone={u['profile_completed']}, OnboardingDone={u['onboarding_completed']}")

print("\nALL HEALTH RECORDS IN DB:")
cur.execute("SELECT * FROM health_record ORDER BY user_id ASC, id ASC")
records = cur.fetchall()
for r in records:
    print(f"HR_ID={r['id']}, UserID={r['user_id']}, Date='{r['date']}', Glucose={r['glucose']}, Meal='{r['meal_context']}', Stress={r['stress']}, Sleep={r['sleep']}, Steps={r['steps']}, Ex={r['exercise_duration']}, Wt={r['weight']}, Mood='{r['mood']}'")

conn.close()
