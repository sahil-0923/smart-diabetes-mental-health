import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("smart_health.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get the latest user created (User ID 2 is akash / rowohep963@limtu.com, User ID 7 is New Guy)
cur.execute("SELECT * FROM user WHERE id = 2")
u2 = cur.fetchone()
print("USER 2 DETAILS:")
print(dict(u2))

cur.execute("SELECT * FROM health_record WHERE user_id = 2 ORDER BY date ASC")
u2_recs = cur.fetchall()
print(f"\nUSER 2 HEALTH RECORDS ({len(u2_recs)}):")
for r in u2_recs:
    print(dict(r))

# Calculate actual metrics for User 2:
glucoses = [r['glucose'] for r in u2_recs if r['glucose'] is not None]
stresses = [r['stress'] for r in u2_recs if r['stress'] is not None]
sleeps = [r['sleep'] for r in u2_recs if r['sleep'] is not None]

print("\nUSER 2 ACTUAL DATABASE CALCULATED METRICS:")
print(f"Latest Glucose: {glucoses[-1] if glucoses else None}")
print(f"Average Glucose: {sum(glucoses)/len(glucoses) if glucoses else None:.1f}")
print(f"Average Stress: {sum(stresses)/len(stresses) if stresses else None:.1f}")
print(f"Average Sleep: {sum(sleeps)/len(sleeps) if sleeps else None:.1f}")
print(f"Latest Check-in Date: {u2_recs[-1]['date'] if u2_recs else None}")
print(f"Latest Check-in Meal: {u2_recs[-1]['meal_context'] if u2_recs else None}")
print(f"Latest Check-in Weight: {u2_recs[-1]['weight'] if u2_recs else None}")
print(f"User Diabetes Type: {u2['diabetes_type']}")
print(f"User Years Diagnosed: {u2['years_since_diagnosis']}")
print(f"User HbA1c: {u2['hba1c']}")

conn.close()
