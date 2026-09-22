import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert the onboarding fields after the `goal` column
fields = """
    profile_completed = db.Column(db.Boolean, default=False)
    onboarding_completed = db.Column(db.Boolean, default=False)
    gender = db.Column(db.String(50))
    years_since_diagnosis = db.Column(db.Integer)
    hba1c = db.Column(db.Float)
    current_medication = db.Column(db.String(255))
    blood_pressure = db.Column(db.String(50))
    cholesterol = db.Column(db.Float)
    smoking_status = db.Column(db.String(50))
    typical_sleep = db.Column(db.Float)
    typical_stress = db.Column(db.Integer)
"""

# check if we already inserted it
if 'profile_completed = db.Column' not in content:
    content = content.replace(
        '    goal = db.Column(\n        db.String(100),\n        default="General wellness"\n    )',
        '    goal = db.Column(\n        db.String(100),\n        default="General wellness"\n    )\n' + fields
    )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fields added to User class in app.py")
