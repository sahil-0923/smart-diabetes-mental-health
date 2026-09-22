import sqlite3
import shutil
import os

db_path = 'smart_health.db'
backup_path = 'smart_health_backup_1F.db'

if not os.path.exists(backup_path):
    shutil.copy2(db_path, backup_path)
    print("Database backed up.")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(user)")
columns = [col[1] for col in cursor.fetchall()]

new_columns = {
    'profile_completed': 'BOOLEAN DEFAULT 0',
    'onboarding_completed': 'BOOLEAN DEFAULT 0',
    'age': 'INTEGER',
    'gender': 'TEXT',
    'height': 'REAL',
    'weight': 'REAL',
    'diabetes_type': 'TEXT',
    'years_since_diagnosis': 'INTEGER',
    'hba1c': 'REAL',
    'current_medication': 'TEXT',
    'blood_pressure': 'TEXT',
    'cholesterol': 'REAL',
    'smoking_status': 'TEXT',
    'activity_level': 'TEXT',
    'typical_sleep': 'REAL',
    'typical_stress': 'INTEGER'
}

for col_name, col_type in new_columns.items():
    if col_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError as e:
            print(f"Error adding {col_name}: {e}")

# Note: for existing users we will leave profile_completed as 0 (False) so they can complete it.
# Wait, the prompt says: "Existing users must not be broken. If their profile is incomplete: Allow them to complete the missing information. Do not erase their existing HealthRecords."
conn.commit()
conn.close()
print("Database migration complete.")
