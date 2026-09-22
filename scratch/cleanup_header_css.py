import os
import re

templates = [
    "templates/dashboard.html",
    "templates/glucose.html",
    "templates/monitoring.html",
    "templates/ai_forecast.html",
    "templates/simulator.html",
    "templates/risk_trends.html",
    "templates/health_trends.html",
    "templates/mental_wellness.html",
    "templates/forecast.html"
]

for tpath in templates:
    if not os.path.exists(tpath):
        continue
    with open(tpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove old search / emergency / top-actions CSS
    content = re.sub(r'\.search-box\s*\{[^}]*\}', '', content)
    content = re.sub(r'\.emergency-btn\s*\{[^}]*\}', '', content)
    content = re.sub(r'\.top-demo-warning\s*\{[^}]*\}', '', content)
    content = re.sub(r'\.top-actions\s*\{[^}]*\}', '', content)

    with open(tpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Cleaned CSS in {tpath}")

print("Done cleaning header CSS!")
