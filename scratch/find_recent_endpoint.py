with open("app.py", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if "health-records" in line or "recent-records" in line or "recent" in line.lower() and "@app.route" in line:
            print(f"Line {idx}: {line.strip()}")
