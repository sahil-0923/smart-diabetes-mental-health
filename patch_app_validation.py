import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update HealthRecord model class to include is_valid and validation_notes
old_hr_model = """class HealthRecord(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    glucose = db.Column(
        db.Float,
        nullable=True
    )

    stress = db.Column(
        db.Float,
        nullable=True
    )

    sleep = db.Column(
        db.Float,
        nullable=True
    )

    steps = db.Column(
        db.Integer,
        nullable=True
    )

    weight = db.Column(
        db.Float,
        nullable=True
    )

    mood = db.Column(
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

new_hr_model = """class HealthRecord(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    glucose = db.Column(
        db.Float,
        nullable=True
    )

    stress = db.Column(
        db.Float,
        nullable=True
    )

    sleep = db.Column(
        db.Float,
        nullable=True
    )

    steps = db.Column(
        db.Integer,
        nullable=True
    )

    weight = db.Column(
        db.Float,
        nullable=True
    )

    mood = db.Column(
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
    )

    is_valid = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    validation_notes = db.Column(
        db.String(255),
        nullable=True
    )"""

code = code.replace(old_hr_model, new_hr_model)

# 2. Add validation function
val_func_code = """
def validate_health_values(glucose=None, stress=None, sleep=None, steps=None, exercise_duration=None, weight=None):
    errors = []
    if glucose is not None and glucose != "":
        try:
            g = float(glucose)
            if g < 40.0 or g > 500.0:
                errors.append(f"Glucose value ({g} mg/dL) is outside valid physiological range (40 - 500 mg/dL).")
        except (ValueError, TypeError):
            errors.append("Glucose must be a valid number.")
            
    if stress is not None and stress != "":
        try:
            s = float(stress)
            if s < 1.0 or s > 10.0:
                errors.append(f"Stress level ({s}) must be between 1 and 10.")
        except (ValueError, TypeError):
            errors.append("Stress level must be a valid number.")
            
    if sleep is not None and sleep != "":
        try:
            sl = float(sleep)
            if sl < 0.5 or sl > 24.0:
                errors.append(f"Sleep hours ({sl}h) must be between 0.5 and 24 hours.")
        except (ValueError, TypeError):
            errors.append("Sleep hours must be a valid number.")
            
    if steps is not None and steps != "":
        try:
            st = int(float(steps))
            if st < 0 or st > 100000:
                errors.append("Steps must be between 0 and 100,000.")
        except (ValueError, TypeError):
            errors.append("Steps must be a valid integer.")
            
    if exercise_duration is not None and exercise_duration != "":
        try:
            ex = float(exercise_duration)
            if ex < 0 or ex > 720:
                errors.append("Exercise duration must be between 0 and 720 minutes.")
        except (ValueError, TypeError):
            errors.append("Exercise duration must be a valid number.")
            
    if weight is not None and weight != "":
        try:
            w = float(weight)
            if w < 20.0 or w > 400.0:
                errors.append("Weight must be between 20 and 400 kg.")
        except (ValueError, TypeError):
            errors.append("Weight must be a valid number.")
            
    return errors
"""

# Insert validation function after db models
code = code.replace(new_hr_model, new_hr_model + "\n" + val_func_code)

# 3. Update add_health route with validation
old_add_health = """@app.route(
    "/add-health",
    methods=[
        "POST"
    ]
)
@login_required
def add_health():
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

new_add_health = """@app.route(
    "/add-health",
    methods=[
        "POST"
    ]
)
@login_required
def add_health():
    user = get_current_user()

    glucose = safe_float(request.form.get("glucose"))
    stress = safe_float(request.form.get("stress"))
    sleep = safe_float(request.form.get("sleep"))
    steps = safe_int(request.form.get("steps"))
    weight = safe_float(request.form.get("weight"))
    mood = clean_text(request.form.get("mood"))
    meal_context = clean_text(request.form.get("meal_context")) or "Random"
    exercise_duration = safe_float(request.form.get("exercise_duration"))

    val_errors = validate_health_values(
        glucose=glucose,
        stress=stress,
        sleep=sleep,
        steps=steps,
        exercise_duration=exercise_duration,
        weight=weight
    )

    if val_errors:
        for err in val_errors:
            flash(err, "error")
        return redirect(url_for("monitoring"))

    record = HealthRecord(
        user_id=user.id,
        date=datetime.utcnow(),
        glucose=glucose,
        stress=stress,
        sleep=sleep,
        steps=steps,
        weight=weight,
        mood=mood,
        meal_context=meal_context,
        exercise_duration=exercise_duration,
        is_valid=True,
        validation_notes="Valid"
    )

    db.session.add(record)
    db.session.commit()

    flash("Health check-in saved successfully.", "success")
    return redirect(url_for("dashboard"))"""

code = code.replace(old_add_health, new_add_health)

# 4. Update onboarding_history with validation
old_onboarding_history = """@app.route('/onboarding/history', methods=['GET', 'POST'])
@login_required
def onboarding_history():
    user = get_current_user()
    if not user.profile_completed:
        return redirect(url_for('onboarding_profile'))
        
    if request.method == 'POST':
        # Simple array processing for 7 days
        dates = request.form.getlist('date[]')
        glucoses = request.form.getlist('glucose[]')
        stresses = request.form.getlist('stress[]')
        sleeps = request.form.getlist('sleep[]')
        steps_list = request.form.getlist('steps[]')
        weights = request.form.getlist('weight[]')
        moods = request.form.getlist('mood[]')
        meals = request.form.getlist('meal_context[]')
        exercises = request.form.getlist('exercise_duration[]')
        
        from datetime import datetime
        for i in range(len(dates)):
            if not dates[i] or not glucoses[i]: continue
            
            try:
                ts = datetime.strptime(dates[i], '%Y-%m-%dT%H:%M')
            except ValueError:
                ts = datetime.now()
                
            hr = HealthRecord(
                user_id=user.id,
                date=datetime.strptime(dates[i][:10], '%Y-%m-%d').date(), # compatibility if needed
                glucose=float(glucoses[i]) if glucoses[i] else 0.0,
                stress=float(stresses[i]) if stresses[i] else 0.0,
                sleep=float(sleeps[i]) if sleeps[i] else 0.0,
                steps=int(steps_list[i]) if steps_list[i] else 0,
                weight=float(weights[i]) if weights[i] else 0.0,
                mood=moods[i] if moods[i] else '5',
                meal_context=meals[i] if meals[i] else 'Random',
                exercise_duration=float(exercises[i]) if exercises[i] else 0.0
            )
            # Actually we want proper timestamp
            hr.timestamp = ts
            db.session.add(hr)
            
        user.onboarding_completed = True
        db.session.commit()
        return redirect(url_for('onboarding_review'))
        
    return render_template('onboarding_history.html', user=user)"""

new_onboarding_history = """@app.route('/onboarding/history', methods=['GET', 'POST'])
@login_required
def onboarding_history():
    user = get_current_user()
    if not user.profile_completed:
        return redirect(url_for('onboarding_profile'))
        
    if request.method == 'POST':
        dates = request.form.getlist('date[]')
        glucoses = request.form.getlist('glucose[]')
        stresses = request.form.getlist('stress[]')
        sleeps = request.form.getlist('sleep[]')
        steps_list = request.form.getlist('steps[]')
        weights = request.form.getlist('weight[]')
        moods = request.form.getlist('mood[]')
        meals = request.form.getlist('meal_context[]')
        exercises = request.form.getlist('exercise_duration[]')
        
        records_to_add = []
        validation_errors = []
        
        for i in range(len(dates)):
            if not dates[i] or not glucoses[i]: continue
            
            raw_g = glucoses[i]
            raw_str = stresses[i] if i < len(stresses) else None
            raw_slp = sleeps[i] if i < len(sleeps) else None
            raw_stp = steps_list[i] if i < len(steps_list) else None
            raw_ex = exercises[i] if i < len(exercises) else None
            raw_wt = weights[i] if i < len(weights) else None
            
            errs = validate_health_values(
                glucose=raw_g,
                stress=raw_str,
                sleep=raw_slp,
                steps=raw_stp,
                exercise_duration=raw_ex,
                weight=raw_wt
            )
            if errs:
                validation_errors.extend([f"Reading {i+1}: {e}" for e in errs])
                continue
                
            try:
                ts = datetime.strptime(dates[i], '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    ts = datetime.strptime(dates[i], '%Y-%m-%d')
                except ValueError:
                    ts = datetime.utcnow()
                    
            hr = HealthRecord(
                user_id=user.id,
                date=ts,
                glucose=float(raw_g),
                stress=float(raw_str) if raw_str else 3.0,
                sleep=float(raw_slp) if raw_slp else 7.5,
                steps=int(float(raw_stp)) if raw_stp else 5000,
                weight=float(raw_wt) if raw_wt else (user.weight or 70.0),
                mood=moods[i] if i < len(moods) and moods[i] else '5',
                meal_context=meals[i] if i < len(meals) and meals[i] else 'Random',
                exercise_duration=float(raw_ex) if raw_ex else 30.0,
                is_valid=True,
                validation_notes="Valid"
            )
            records_to_add.append(hr)
            
        if validation_errors:
            for err in validation_errors:
                flash(err, "error")
            return render_template('onboarding_history.html', user=user)
            
        if len(records_to_add) < 5:
            flash("Please enter at least 5 valid health readings to establish your baseline.", "error")
            return render_template('onboarding_history.html', user=user)
            
        for r in records_to_add:
            db.session.add(r)
            
        user.onboarding_completed = True
        db.session.commit()
        return redirect(url_for('onboarding_review'))
        
    return render_template('onboarding_history.html', user=user)"""

code = code.replace(old_onboarding_history, new_onboarding_history)

# 5. Update api/health/summary, api/glucose/history, api/glucose/trend, api/wellness/history, api/health-trends, api/forecast/predict to filter on is_valid=True
old_api_summary = """@app.route("/api/health/summary")
@login_required
def api_health_summary():
    user = get_current_user()
    
    # Latest record
    latest = HealthRecord.query.filter(HealthRecord.user_id == user.id).order_by(HealthRecord.date.desc()).first()
    if not latest:
        return jsonify({"success": True, "records": [], "message": "No health records available yet."})
        
    # Today's glucose
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.date >= today,
        HealthRecord.glucose.isnot(None)
    ).all()
    
    today_avg = sum([r.glucose for r in today_records]) / len(today_records) if today_records else None
    
    # Weekly glucose
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.date >= week_ago,
        HealthRecord.glucose.isnot(None)
    ).all()
    
    weekly_avg = sum([r.glucose for r in weekly_records]) / len(weekly_records) if weekly_records else None
    highest = max([r.glucose for r in weekly_records]) if weekly_records else (latest.glucose if latest else None)
    lowest = min([r.glucose for r in weekly_records]) if weekly_records else (latest.glucose if latest else None)
    
    return jsonify({
        "success": True,
        "current_glucose": latest.glucose,
        "today_average_glucose": round(today_avg, 1) if today_avg else None,
        "weekly_average_glucose": round(weekly_avg, 1) if weekly_avg else None,
        "highest_recent_glucose": highest,
        "lowest_recent_glucose": lowest,
        "latest_stress": latest.stress,
        "latest_sleep": latest.sleep,
        "latest_steps": latest.steps,
        "latest_weight": latest.weight,
        "latest_mood": latest.mood
    })"""

new_api_summary = """@app.route("/api/health/summary")
@login_required
def api_health_summary():
    user = get_current_user()
    
    # All valid records for user
    valid_records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.is_valid == True
    ).order_by(HealthRecord.date.desc()).all()
    
    if not valid_records:
        return jsonify({"success": True, "records": [], "message": "No valid health records available yet."})
        
    latest = valid_records[0]
    prev = valid_records[1] if len(valid_records) > 1 else None
    
    # Delta
    delta = round(latest.glucose - prev.glucose, 1) if (prev and latest.glucose is not None and prev.glucose is not None) else None
    
    # Today's glucose
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_records = [r for r in valid_records if r.date and r.date >= today and r.glucose is not None]
    today_avg = round(sum([r.glucose for r in today_records]) / len(today_records), 1) if today_records else None
    
    # Weekly glucose (last 7 days or all valid records if historical)
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_records = [r for r in valid_records if r.date and r.date >= week_ago and r.glucose is not None]
    if not weekly_records:
        weekly_records = [r for r in valid_records if r.glucose is not None]
        
    all_glucoses = [r.glucose for r in weekly_records if r.glucose is not None]
    weekly_avg = round(sum(all_glucoses) / len(all_glucoses), 1) if all_glucoses else None
    highest = max(all_glucoses) if all_glucoses else latest.glucose
    lowest = min(all_glucoses) if all_glucoses else latest.glucose
    
    all_stress = [r.stress for r in valid_records if r.stress is not None]
    stress_avg = round(sum(all_stress) / len(all_stress), 1) if all_stress else latest.stress
    
    all_sleep = [r.sleep for r in valid_records if r.sleep is not None]
    sleep_avg = round(sum(all_sleep) / len(all_sleep), 1) if all_sleep else latest.sleep

    return jsonify({
        "success": True,
        "current_glucose": latest.glucose,
        "previous_glucose": prev.glucose if prev else None,
        "glucose_delta": delta,
        "today_average_glucose": today_avg,
        "weekly_average_glucose": weekly_avg,
        "highest_recent_glucose": highest,
        "lowest_recent_glucose": lowest,
        "latest_stress": latest.stress,
        "stress_average": stress_avg,
        "latest_sleep": latest.sleep,
        "sleep_average": sleep_avg,
        "latest_steps": latest.steps,
        "latest_weight": latest.weight,
        "latest_mood": latest.mood,
        "latest_meal": latest.meal_context,
        "latest_timestamp": latest.date.strftime("%Y-%m-%d %H:%M:%S") if latest.date else None
    })"""

code = code.replace(old_api_summary, new_api_summary)

# 6. Update api_glucose_history to filter is_valid=True
old_api_glucose = """@app.route("/api/glucose/history")
@login_required
def api_glucose_history():
    user = get_current_user()
    try:
        days = int(request.args.get('days', 7))
        if days <= 0 or days > 365:
            days = 7
    except ValueError:
        days = 7

    cutoff = datetime.utcnow() - timedelta(days=days)
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.date >= cutoff
    ).order_by(HealthRecord.date.asc()).all()
    
    if not records:
        return jsonify({"success": True, "records": [], "message": "No health records available yet."})

    glucose_records = [r for r in records if r.glucose is not None]
    
    if not glucose_records:
        return jsonify({"success": True, "records": [], "message": "No glucose records available yet."})

    labels = [r.date.strftime("%Y-%m-%d %H:%M") for r in glucose_records]
    values = [r.glucose for r in glucose_records]
    
    stats = {}
    if glucose_records:
        stats["current"] = glucose_records[-1].glucose
        stats["average"] = round(sum(values) / len(values), 1)
        stats["highest"] = max(values)
        stats["lowest"] = min(values)

    return jsonify({
        "success": True,
        "labels": labels,
        "values": values,
        "stats": stats
    })"""

new_api_glucose = """@app.route("/api/glucose/history")
@login_required
def api_glucose_history():
    user = get_current_user()
    try:
        days = int(request.args.get('days', 7))
        if days <= 0 or days > 365:
            days = 7
    except ValueError:
        days = 7

    cutoff = datetime.utcnow() - timedelta(days=days)
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.is_valid == True,
        HealthRecord.date >= cutoff
    ).order_by(HealthRecord.date.asc()).all()
    
    # If no records in cutoff, load all valid records
    if not records:
        records = HealthRecord.query.filter(
            HealthRecord.user_id == user.id,
            HealthRecord.is_valid == True
        ).order_by(HealthRecord.date.asc()).all()
    
    glucose_records = [r for r in records if r.glucose is not None]
    
    if not glucose_records:
        return jsonify({"success": True, "labels": [], "values": [], "stats": {}, "message": "No valid glucose records available."})

    labels = [r.date.strftime("%Y-%m-%d %H:%M") if r.date else "" for r in glucose_records]
    values = [r.glucose for r in glucose_records]
    
    prev_val = glucose_records[-2].glucose if len(glucose_records) > 1 else None
    curr_val = glucose_records[-1].glucose
    delta = round(curr_val - prev_val, 1) if prev_val is not None else None

    stats = {
        "current": curr_val,
        "previous": prev_val,
        "delta": delta,
        "average": round(sum(values) / len(values), 1),
        "highest": max(values),
        "lowest": min(values)
    }

    return jsonify({
        "success": True,
        "labels": labels,
        "values": values,
        "stats": stats
    })"""

code = code.replace(old_api_glucose, new_api_glucose)

# 7. Update api_glucose_trend
old_api_trend = """@app.route("/api/glucose/trend")
@login_required
def api_glucose_trend():
    user = get_current_user()
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.glucose.isnot(None)
    ).order_by(HealthRecord.date.desc()).limit(10).all()

    if not records or len(records) < 2:
        return jsonify({
            "status": "Insufficient Data",
            "trend": "unknown",
            "message": "Need at least 2 readings to calculate trend."
        })

    # latest first, so reverse to chronological
    chrono = list(reversed(records))
    first = chrono[0].glucose
    last = chrono[-1].glucose
    diff = last - first

    if diff > 10:
        trend = "Increasing"
        color = "#ef4444"
        desc = f"Your glucose has increased by {abs(diff):.1f} mg/dL over recent readings."
    elif diff < -10:
        trend = "Decreasing"
        color = "#10b981"
        desc = f"Your glucose has decreased by {abs(diff):.1f} mg/dL over recent readings."
    else:
        trend = "Stable"
        color = "#3b82f6"
        desc = "Your glucose levels are stable."

    return jsonify({
        "status": trend,
        "difference": round(diff, 1),
        "color": color,
        "description": desc,
        "count": len(records)
    })"""

new_api_trend = """@app.route("/api/glucose/trend")
@login_required
def api_glucose_trend():
    user = get_current_user()
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.is_valid == True,
        HealthRecord.glucose.isnot(None)
    ).order_by(HealthRecord.date.desc()).limit(10).all()

    if not records or len(records) == 0:
        return jsonify({
            "status": "No data yet",
            "direction": "none",
            "color": "#64748b",
            "description": "No valid glucose readings recorded yet.",
            "count": 0
        })

    if len(records) == 1:
        return jsonify({
            "status": "Baseline recorded",
            "direction": "none",
            "color": "#3b82f6",
            "description": "1 valid reading recorded. Add more readings to calculate glucose trajectory.",
            "count": 1
        })

    # Chronological order
    chrono = list(reversed(records))
    first = chrono[0].glucose
    last = chrono[-1].glucose
    diff = last - first

    if diff > 5.0:
        trend = "Increasing"
        color = "#f59e0b"
        direction = "up"
        desc = f"Glucose has increased by {abs(diff):.1f} mg/dL across recent readings."
    elif diff < -5.0:
        trend = "Decreasing"
        color = "#10b981"
        direction = "down"
        desc = f"Glucose has decreased by {abs(diff):.1f} mg/dL across recent readings."
    else:
        trend = "Stable"
        color = "#3b82f6"
        direction = "stable"
        desc = "Glucose levels are relatively steady across recent readings."

    return jsonify({
        "status": trend,
        "direction": direction,
        "difference": round(diff, 1),
        "color": color,
        "description": desc,
        "count": len(records)
    })"""

code = code.replace(old_api_trend, new_api_trend)

# 8. Update Forecast APIs to filter is_valid=True
code = code.replace(
    'records = HealthRecord.query.filter_by(user_id=user.id).order_by(HealthRecord.date.asc()).all()',
    'records = HealthRecord.query.filter_by(user_id=user.id, is_valid=True).order_by(HealthRecord.date.asc()).all()'
)

# 9. Update recent records and wellness history to filter is_valid=True
code = code.replace(
    'HealthRecord.user_id == user.id',
    'HealthRecord.user_id == user.id, HealthRecord.is_valid == True'
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("app.py successfully patched with data validation and clean queries!")
