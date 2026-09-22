import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update HealthRecord model
new_columns = """    mood = db.Column(
        db.String(50),
        nullable=True
    )

    meal_context = db.Column(
        db.String(50),
        nullable=True
    )

    exercise_duration = db.Column(
        db.Float,
        nullable=True
    )"""

content = re.sub(r'    mood = db\.Column\(\s*db\.String\(50\),\s*nullable=True\s*\)', new_columns, content)


# Update add_health route
new_add_health = """def add_health():

    user = get_current_user()

    glucose = safe_float(request.form.get("glucose"))
    stress = safe_float(request.form.get("stress"))
    sleep = safe_float(request.form.get("sleep"))
    steps = safe_int(request.form.get("steps"))
    weight = safe_float(request.form.get("weight"))
    
    # Existing code used clean_text for mood
    mood = clean_text(request.form.get("mood"))
    
    # New fields
    meal_context = clean_text(request.form.get("meal_context")) or "Random"
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
    return redirect(url_for("dashboard"))"""

pattern = re.compile(r'def add_health\(\):.*?return redirect\(\s*url_for\("dashboard"\)\s*\)', re.DOTALL)
content = pattern.sub(new_add_health, content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.py successfully")
