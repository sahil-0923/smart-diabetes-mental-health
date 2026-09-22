import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

lines = text.split("\n")
routes = []
for i, line in enumerate(lines):
    if line.strip().startswith("@app.route("):
        route_str = line.strip()
        # look ahead for def
        for j in range(i+1, min(i+10, len(lines))):
            if lines[j].strip().startswith("def "):
                fn_name = lines[j].strip().split("(")[0].replace("def ", "")
                routes.append((route_str, fn_name, j+1))
                break

for r in routes:
    if any(k in r[0] for k in ['dashboard', 'forecast', 'glucose', 'risk', 'sim', 'monitoring', 'health', 'predict']):
        print(f"Line {r[2]}: {r[0]} -> {r[1]}")
