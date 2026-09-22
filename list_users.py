import sqlite3

conn = sqlite3.connect("smart_health.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id, name, email, age, gender, height, weight, diabetes_type, years_since_diagnosis, hba1c, current_medication, blood_pressure, cholesterol, smoking_status, activity_level, typical_sleep, typical_stress, profile_completed, onboarding_completed FROM user")
users = cur.fetchall()
for u in users:
    print(dict(u))

conn.close()
