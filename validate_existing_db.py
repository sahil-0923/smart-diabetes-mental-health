import sqlite3

def validate_record_values(glucose, stress, sleep, steps, exercise_duration, weight):
    issues = []
    
    if glucose is not None:
        if glucose < 40.0:
            issues.append(f"Glucose {glucose} mg/dL is below physiological threshold (min 40 mg/dL)")
        elif glucose > 500.0:
            issues.append(f"Glucose {glucose} mg/dL is above physiological threshold (max 500 mg/dL)")
            
    if stress is not None:
        if stress < 1.0 or stress > 10.0:
            issues.append(f"Stress score {stress} is outside valid 1-10 range")
            
    if sleep is not None:
        if sleep < 0.5 or sleep > 24.0:
            issues.append(f"Sleep duration {sleep}h is outside valid 0.5-24h range")
            
    if steps is not None:
        if steps < 0 or steps > 100000:
            issues.append(f"Steps count {steps} is invalid")
            
    if exercise_duration is not None:
        if exercise_duration < 0 or exercise_duration > 720:
            issues.append(f"Exercise duration {exercise_duration}m is invalid")
            
    if weight is not None:
        if weight < 20.0 or weight > 400.0:
            issues.append(f"Weight {weight}kg is invalid")

    is_valid = len(issues) == 0
    notes = "; ".join(issues) if issues else "Valid"
    return is_valid, notes

conn = sqlite3.connect("smart_health.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id, user_id, date, glucose, stress, sleep, steps, exercise_duration, weight FROM health_record")
rows = cur.fetchall()

valid_count = 0
invalid_count = 0

print("AUDITING AND UPDATING EXISTING HEALTH RECORDS:")
for r in rows:
    is_valid, notes = validate_record_values(
        r["glucose"], r["stress"], r["sleep"], r["steps"], r["exercise_duration"], r["weight"]
    )
    cur.execute(
        "UPDATE health_record SET is_valid = ?, validation_notes = ? WHERE id = ?",
        (1 if is_valid else 0, notes, r["id"])
    )
    if is_valid:
        valid_count += 1
    else:
        invalid_count += 1
        print(f"  [INVALID RECORD #{r['id']} (User {r['user_id']})]: {notes}")

conn.commit()
print(f"\nAudit complete! {valid_count} valid records, {invalid_count} flagged as invalid.")

# Check User 2 records specifically
cur.execute("SELECT id, user_id, date, glucose, stress, is_valid, validation_notes FROM health_record WHERE user_id = 2")
for r in cur.fetchall():
    print(f"  User 2 -> HR #{r['id']}: Glucose={r['glucose']}, Stress={r['stress']}, is_valid={r['is_valid']}, Notes={r['validation_notes']}")

conn.close()
