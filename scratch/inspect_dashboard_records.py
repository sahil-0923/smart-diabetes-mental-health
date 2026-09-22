import os
import sys
sys.path.insert(0, os.path.abspath("."))
from app import app, db, User, HealthRecord

with app.app_context():
    users = User.query.all()
    print("USERS IN DATABASE:")
    for u in users:
        records = HealthRecord.query.filter_by(user_id=u.id).order_by(HealthRecord.id.desc()).all()
        print(f"User ID: {u.id}, Name: '{u.name}', Email: '{u.email}', Total Records: {len(records)}")
        for r in records[:10]:
            print(f"  -> Record ID: {r.id}, Date: {r.date}, Glucose: {r.glucose}, Context: '{r.meal_context}', Stress: {r.stress}, Sleep: {r.sleep}, Steps: {r.steps}")
