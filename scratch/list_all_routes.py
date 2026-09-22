with open("app.py", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if line.strip().startswith("@app.route"):
            print(f"{idx}: {line.strip()}")
