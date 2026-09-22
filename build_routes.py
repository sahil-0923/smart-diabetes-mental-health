import os
import re

app_file = "app.py"

with open(app_file, "r", encoding="utf-8") as f:
    app_code = f.read()

# Replace old /forecast with /ai-forecast if it exists
app_code = app_code.replace('@app.route("/forecast")\n@login_required\ndef forecast():\n    user = get_current_user()\n    return render_template("forecast.html", user=user)', '')

routes = """
@app.route("/glucose")
@login_required
def glucose(): return render_template("glucose.html", user=get_current_user())

@app.route("/ai-forecast")
@login_required
def ai_forecast(): return render_template("ai_forecast.html", user=get_current_user())

@app.route("/risk-trends")
@login_required
def risk_trends(): return render_template("risk_trends.html", user=get_current_user())

@app.route("/simulator")
@login_required
def simulator(): return render_template("simulator.html", user=get_current_user())

@app.route("/mental-wellness")
@login_required
def mental_wellness(): return render_template("mental_wellness.html", user=get_current_user())

@app.route("/health-trends")
@login_required
def health_trends(): return render_template("health_trends.html", user=get_current_user())
"""

if 'def glucose():' not in app_code:
    app_code = app_code.replace('# ============================================================\n# DASHBOARD', routes + '\n\n# ============================================================\n# DASHBOARD')
    with open(app_file, "w", encoding="utf-8") as f:
        f.write(app_code)

print("Updated app.py routes.")
