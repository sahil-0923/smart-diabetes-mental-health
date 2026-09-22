import os
import sys
sys.path.insert(0, os.path.abspath("."))
from app import app, db, User, HealthRecord

with app.app_context():
    # Remove records for User 99889
    recs = HealthRecord.query.filter_by(user_id=99889).all()
    print(f"Deleting {len(recs)} records for user 99889")
    for r in recs:
        db.session.delete(r)
    u = User.query.get(99889)
    if u:
        print(f"Deleting User 99889 ({u.email})")
        db.session.delete(u)
    db.session.commit()

    # Verify user 99890 (Rahul Kumar)
    u90 = User.query.filter_by(name="Rahul Kumar").first()
    print(f"\nActive Rahul Kumar: ID={u90.id}, email={u90.email}")
    recs90 = HealthRecord.query.filter_by(user_id=u90.id).order_by(HealthRecord.date.desc()).all()
    print(f"Total valid records: {len(recs90)}")
    for r in recs90:
        print(f"  Record {r.id}: {r.date} | {r.glucose} mg/dL | Context: {r.meal_context}")
