import os
import re

# Clean DEMO badges across all templates
template_files = [
    "templates/dashboard.html",
    "templates/glucose.html",
    "templates/ai_forecast.html",
    "templates/risk_trends.html",
    "templates/simulator.html",
    "templates/monitoring.html",
    "templates/health_trends.html",
    "templates/mental_wellness.html"
]

for tf in template_files:
    if os.path.exists(tf):
        with open(tf, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove demo badge spans
        content = re.sub(r'<span class="badge-demo"[^>]*>DEMO</span>', '', content)
        content = re.sub(r'<span class="demo-badge"[^>]*>DEMO</span>', '', content)
        content = re.sub(r'<span class="badge-new"[^>]*>NEW</span>', '', content)
        content = content.replace("Demo data shown throughout.", "Health records shown are user-entered records stored in the application database. AI forecasts and risk indicators are research outputs and are not medical diagnoses.")
        
        with open(tf, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned {tf}")

print("All targeted consistency and dynamic spike updates applied!")
