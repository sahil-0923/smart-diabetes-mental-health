import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_apis = """
# ============================================================
# NEW UI DATA APIs (PHASE 1C)
# ============================================================
from datetime import timedelta

@app.route("/api/glucose/history")
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
        "days": days,
        "labels": labels,
        "values": values,
        "records": [{"id": r.id, "timestamp": r.date.strftime("%Y-%m-%d %H:%M"), "glucose": r.glucose} for r in glucose_records],
        "statistics": stats
    })

@app.route("/api/glucose/trend")
@login_required
def api_glucose_trend():
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
        HealthRecord.date >= cutoff,
        HealthRecord.glucose.isnot(None)
    ).order_by(HealthRecord.date.asc()).all()

    if len(records) < 2:
        return jsonify({"success": True, "trend": "stable", "change": 0.0, "records_used": len(records)})

    # Simple trend calculation: average of first half vs average of second half
    half = len(records) // 2
    first_half = [r.glucose for r in records[:half]]
    second_half = [r.glucose for r in records[half:]]
    
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    
    change = round(avg_second - avg_first, 2)
    
    if change > 5.0:
        trend = "increasing"
    elif change < -5.0:
        trend = "decreasing"
    else:
        trend = "stable"

    return jsonify({
        "success": True,
        "trend": trend,
        "change": change,
        "records_used": len(records)
    })

@app.route("/api/wellness/history")
@login_required
def api_wellness_history():
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
        return jsonify({"success": True, "records": [], "message": "No wellness records available yet."})

    labels = [r.date.strftime("%Y-%m-%d %H:%M") for r in records]
    
    return jsonify({
        "success": True,
        "labels": labels,
        "stress": [r.stress for r in records],
        "sleep": [r.sleep for r in records],
        "mood": [r.mood for r in records],
        "steps": [r.steps for r in records],
        "exercise_duration": [r.exercise_duration for r in records]
    })

@app.route("/api/health-trends")
@login_required
def api_health_trends():
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
        return jsonify({"success": True, "records": [], "message": "No health trends available yet."})

    labels = [r.date.strftime("%Y-%m-%d %H:%M") for r in records]

    return jsonify({
        "success": True,
        "labels": labels,
        "glucose": [r.glucose for r in records],
        "stress": [r.stress for r in records],
        "sleep": [r.sleep for r in records],
        "steps": [r.steps for r in records],
        "weight": [r.weight for r in records],
        "mood": [r.mood for r in records],
        "exercise_duration": [r.exercise_duration for r in records]
    })

@app.route("/api/health-records/recent")
@login_required
def api_recent_health_records():
    user = get_current_user()
    try:
        limit = int(request.args.get('limit', 10))
        if limit <= 0 or limit > 100:
            limit = 10
    except ValueError:
        limit = 10

    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id
    ).order_by(HealthRecord.date.desc()).limit(limit).all()

    if not records:
        return jsonify({"success": True, "records": [], "message": "No health records available yet."})

    ret_records = []
    for r in records:
        ret_records.append({
            "id": r.id,
            "timestamp": r.date.strftime("%Y-%m-%d %H:%M:%S"),
            "glucose": r.glucose,
            "stress": r.stress,
            "sleep": r.sleep,
            "steps": r.steps,
            "weight": r.weight,
            "mood": r.mood,
            "meal_context": r.meal_context,
            "exercise_duration": r.exercise_duration
        })

    return jsonify({
        "success": True,
        "records": ret_records
    })

@app.route("/api/health/summary")
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
    highest = max([r.glucose for r in weekly_records]) if weekly_records else None
    lowest = min([r.glucose for r in weekly_records]) if weekly_records else None
    
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
    })

"""

content = content.replace('if __name__ == "__main__":', new_apis + '\nif __name__ == "__main__":')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Injected APIs successfully.")
