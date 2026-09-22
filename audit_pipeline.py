import sqlite3
import re
from datetime import datetime

print("================================================================")
print("1. DATABASE AUDIT: USERS & HEALTH RECORDS")
print("================================================================")

conn = sqlite3.connect("smart_health.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get User columns
cur.execute("PRAGMA table_info(user)")
user_cols = [r["name"] for r in cur.fetchall()]
print(f"User columns in DB: {user_cols}")

# Get all Users
cur.execute("SELECT * FROM user ORDER BY id DESC")
users = cur.fetchall()
print(f"\nTotal Users: {len(users)}")
for u in users:
    print(f"\nUSER ID: {u['id']} | Name: {u['name']} | Email: {u['email']}")
    for col in user_cols:
        if col not in ['password']:
            print(f"  {col}: {u[col]}")

# Get HealthRecord columns
cur.execute("PRAGMA table_info(health_record)")
hr_cols = [r["name"] for r in cur.fetchall()]
print(f"\nHealthRecord columns in DB: {hr_cols}")

cur.execute("SELECT * FROM health_record ORDER BY user_id DESC, date ASC")
records = cur.fetchall()
print(f"\nTotal HealthRecords: {len(records)}")
for r in records:
    print(f"  HR ID: {r['id']} | User ID: {r['user_id']} | Date: {r['date']} | Glucose: {r['glucose']} | Meal: {r['meal_context']} | Stress: {r['stress']} | Sleep: {r['sleep']} | Steps: {r['steps']} | Ex: {r['exercise_duration']} | Weight: {r['weight']} | Mood: {r['mood']}")

conn.close()

print("\n================================================================")
print("2. ONBOARDING ROUTES AUDIT IN APP.PY")
print("================================================================")
with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

onboarding_section = re.search(r"@app\.route\(['\"]/onboarding/profile.*?if __name__ == ['\"]__main__['\"]:", code, re.DOTALL)
if onboarding_section:
    print(onboarding_section.group(0))
else:
    print("Could not find onboarding section regex, searching manually:")
    for line in code.split("\n"):
        if "/onboarding" in line:
            print(line)
