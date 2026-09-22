import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('def add_health():')
end = content.find('return redirect(', start)
end = content.find(')', end) + 1

new_add_health = """def add_health():
    user = get_current_user()

    glucose = safe_float(request.form.get("glucose"))
    stress = safe_float(request.form.get("stress"))
    sleep = safe_float(request.form.get("sleep"))
    steps = safe_int(request.form.get("steps"))
    weight = safe_float(request.form.get("weight"))
    mood = clean_text(request.form.get("mood"))
    
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

if start != -1 and end != -1:
    content = content[:start] + new_add_health + content[end:]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated add_health")
else:
    print("Could not find add_health")
