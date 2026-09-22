import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_add_health = """def add_health():

    user = get_current_user()

    glucose = safe_float(request.form.get("glucose"))
    stress = safe_float(request.form.get("stress"))
    sleep = safe_float(request.form.get("sleep"))
    steps = safe_int(request.form.get("steps"))
    weight = safe_float(request.form.get("weight"))
    mood = safe_float(request.form.get("mood"))
    
    # New fields
    meal_context = request.form.get("meal_context", "Random")
    exercise_duration = safe_float(request.form.get("exercise_duration"))

    record = HealthRecord(
        user_id=user.id,
        glucose=glucose,
        stress=stress,
        sleep=sleep,
        steps=steps,
        weight=weight,
        mood=mood,
        meal_context=meal_context,
        exercise_duration=exercise_duration
    )

    db.session.add(record)
    db.session.commit()

    flash("Health check-in saved successfully.", "success")
    return redirect(url_for("dashboard"))
"""

# We need to accurately replace the old def add_health() block
# It goes until return redirect(url_for("dashboard"))
pattern = re.compile(r'def add_health\(\):.*?return redirect\(\s*url_for\("dashboard"\)\s*\)', re.DOTALL)
content = pattern.sub(new_add_health, content)

# We also need to add meal_context and exercise_duration to the HealthRecord model!
# Let's find class HealthRecord(db.Model):
health_record_pattern = re.compile(r'class HealthRecord\(db\.Model\):.*?    mood = db\.Column\(\s*db\.String\(50\),\s*nullable=True\s*\)', re.DOTALL)
# Wait, my ast parse said mood is in the DB. Let's just find the end of the class.
# Let's just inject after `mood = db.Column(...)` or at the end of the block.
# Actually, the simplest way is to just inject before `def get_current_user():` if it exists, or just search for `mood = db.Column(db.String(50), nullable=True)` (or whatever it is).
# Let's check what `mood = ` is first.
