import os
import re

templates = [
    "templates/dashboard.html",
    "templates/glucose.html",
    "templates/monitoring.html",
    "templates/forecast.html",
    "templates/ai_forecast.html",
    "templates/risk_trends.html",
    "templates/simulator.html",
    "templates/health_trends.html",
    "templates/mental_wellness.html"
]

for tpath in templates:
    if not os.path.exists(tpath):
        continue
    with open(tpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove the top-demo-warning block
    content = re.sub(
        r'<div class="top-demo-warning">[\s\S]*?</div>',
        '',
        content
    )
    
    # Remove top-notice block in topbar if present
    content = re.sub(
        r'<div class="top-notice">[\s\S]*?</div>',
        '',
        content
    )

    with open(tpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Removed top warning banner from {tpath}")

print("Done removing top warning banner across all templates!")
