import os
import sys
sys.path.insert(0, os.path.abspath("."))
from app import app, db, User, HealthRecord

with app.app_context():
    # Find test users created with rahul.test2026@example.com
    test_users = User.query.filter(User.email.like("%test2026%")).all()
    print(f"Found {len(test_users)} test2026 users:")
    for tu in test_users:
        recs = HealthRecord.query.filter_by(user_id=tu.id).all()
        print(f"Deleting test user {tu.id} ({tu.email}) with {len(recs)} test records")
        for r in recs:
            db.session.delete(r)
        db.session.delete(tu)
    db.session.commit()
    print("Test users and test records cleaned up.")

    # Show remaining active users
    users = User.query.all()
    print("\nREMAINING USERS:")
    for u in users:
        recs = HealthRecord.query.filter_by(user_id=u.id).order_by(HealthRecord.date.desc()).all()
        print(f"User {u.id}: '{u.name}' ({u.email}) -> {len(recs)} records")
        for r in recs[:5]:
            print(f"   Record {r.id}: {r.date} | {r.glucose} mg/dL | Context: '{r.meal_context}' | Stress: {r.stress}")
