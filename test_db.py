import requests
import sqlite3
import random

BASE_URL = 'http://127.0.0.1:5000'

session = requests.Session()

# 1. Register a test user
register_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'password': 'password123',
    'diabetes_type': 'Type 2'
}
r1 = session.post(f"{BASE_URL}/register", data=register_data)

# 2. Login
login_data = {
    'email': 'testuser@example.com',
    'password': 'password123'
}
r2 = session.post(f"{BASE_URL}/login", data=login_data)

# 3. Submit multiple health records
records = [
    {
        'glucose': '145',
        'stress': '7',
        'sleep': '6.5',
        'steps': '5000',
        'weight': '62',
        'mood': '7',
        'meal_context': 'Post-meal',
        'exercise_duration': '30'
    },
    {
        'glucose': '110',
        'stress': '4',
        'sleep': '8',
        'steps': '10000',
        'weight': '61.5',
        'mood': '9',
        'meal_context': 'Fasting',
        'exercise_duration': '60'
    },
    {
        'glucose': '180',
        'stress': '8',
        'sleep': '5',
        'steps': '2000',
        'weight': '62.2',
        'mood': '4',
        'meal_context': 'Random',
        'exercise_duration': '0'
    }
]

for rec in records:
    r3 = session.post(f"{BASE_URL}/add_health", data=rec)
    print("Submitted record. Status code:", r3.status_code)

# 4. Verify directly in SQLite
conn = sqlite3.connect('smart_health.db')
cursor = conn.cursor()
cursor.execute("SELECT user_id, date, glucose, stress, sleep, steps, weight, mood, meal_context, exercise_duration FROM health_record ORDER BY id DESC LIMIT 3")
rows = cursor.fetchall()
print("\n--- SQLITE VERIFICATION ---")
for row in rows:
    print(row)

# Also check that existing records still exist
cursor.execute("SELECT count(*) FROM health_record")
print("\nTotal Health Records in DB:", cursor.fetchone()[0])
conn.close()
