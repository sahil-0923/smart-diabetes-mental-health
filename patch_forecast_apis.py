# Script to add forecast APIs to app.py
with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Check if forecast routes already exist
if "/api/forecast/predict" not in content:
    route_code = """

# ============================================================
# PHASE 2 - REAL GRU AI FORECAST & SIMULATION APIS
# ============================================================
from ai.model_service import model_service

@app.route("/api/forecast/status", methods=["GET"])
@login_required
def api_forecast_status():
    user = get_current_user()
    records = HealthRecord.query.filter_by(user_id=user.id).order_by(HealthRecord.date.asc()).all()
    return jsonify(model_service.get_status(user_record_count=len(records)))

@app.route("/api/forecast/predict", methods=["POST", "GET"])
@login_required
def api_forecast_predict():
    user = get_current_user()
    records = HealthRecord.query.filter_by(user_id=user.id).order_by(HealthRecord.date.asc()).all()
    result = model_service.predict_forecast(records)
    return jsonify(result)

@app.route("/api/forecast/simulate", methods=["POST"])
@login_required
def api_forecast_simulate():
    user = get_current_user()
    records = HealthRecord.query.filter_by(user_id=user.id).order_by(HealthRecord.date.asc()).all()
    data = request.get_json(silent=True) or request.form
    exercise_mins = float(data.get("exercise_mins", 0))
    sleep_hours = float(data.get("sleep_hours", 7.0))
    meal_context = data.get("meal_context", "Normal")
    result = model_service.simulate_whatif(records, exercise_mins, sleep_hours, meal_context)
    return jsonify(result)

"""
    # Insert right before `if __name__ == "__main__":`
    if 'if __name__ == "__main__":' in content:
        content = content.replace('if __name__ == "__main__":', route_code + '\nif __name__ == "__main__":')
    else:
        content += route_code
        
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Forecast API routes added successfully to app.py.")
else:
    print("Forecast API routes already present in app.py.")
