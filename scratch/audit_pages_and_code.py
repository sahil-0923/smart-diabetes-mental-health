import os
import sys
import re
import json

sys.path.insert(0, os.path.abspath("."))
from bs4 import BeautifulSoup
from app import app, db, User, HealthRecord
from ai.model_service import model_service

def scan_hardcoded_values():
    print("=" * 80)
    print("AUDIT PART 15: HARDCODED / DEMO VALUES SCAN")
    print("=" * 80)
    
    search_terms = ["201", "133.3", "133.6", "138.7", "140.6", "142.6", "demo", "DEMO", "fake"]
    scanned_extensions = [".py", ".html", ".js"]
    ignore_dirs = ["venv", ".git", "scratch", "__pycache__", ".gemini"]
    
    findings = []
    
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in scanned_extensions:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        for idx, line in enumerate(lines, 1):
                            for term in search_terms:
                                if term in line:
                                    findings.append({
                                        "file": filepath,
                                        "line": idx,
                                        "term": term,
                                        "content": line.strip()
                                    })
                except Exception as e:
                    pass
                    
    print(f"Total scan matches found across application: {len(findings)}")
    # Classify matches
    for f in findings[:25]:
        print(f"  {f['file']}:{f['line']} | Term: '{f['term']}' | Content: {f['content'][:70]}")

def audit_simulator():
    print("\n" + "=" * 80)
    print("AUDIT PART 8: WHAT-IF SIMULATOR VERIFICATION")
    print("=" * 80)
    client = app.test_client()
    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        user_id = user.id
        recs = HealthRecord.query.filter_by(user_id=user_id, is_valid=True).order_by(HealthRecord.date.asc()).all()
        
        sim_res = model_service.simulate_whatif(recs, exercise_mins=30, sleep_hours=8.0, meal_context="Normal")
        print("Model Service simulate_whatif output:")
        print(json.dumps(sim_res, indent=2))
        
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    sim_post = client.post("/api/forecast/simulate", json={"exercise_mins": 45, "sleep_hours": 7.5, "meal_context": "Low Carb"})
    print("\nAPI /api/forecast/simulate output:")
    print(sim_post.get_json())

def audit_ai_forecast_page():
    print("\n" + "=" * 80)
    print("AUDIT PART 7: AI FORECAST PAGE & PIPELINE PARITY")
    print("=" * 80)
    client = app.test_client()
    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        user_id = user.id
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        
    resp = client.get("/api/forecast/predict")
    print("API /api/forecast/predict output:")
    print(resp.get_json())
    
    page = client.get("/ai-forecast")
    print(f"/ai-forecast page HTTP status: {page.status_code}")

if __name__ == "__main__":
    scan_hardcoded_values()
    audit_simulator()
    audit_ai_forecast_page()
