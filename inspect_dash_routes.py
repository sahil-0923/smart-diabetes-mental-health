with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

import re

routes_to_check = [
    r"@app\.route\(['\"]/dashboard['\"].*?def \w+\(.*?\):.*?(?=@app\.route|\Z)",
    r"@app\.route\(['\"]/api/health/summary['\"].*?def \w+\(.*?\):.*?(?=@app\.route|\Z)",
    r"@app\.route\(['\"]/api/health-records/recent['\"].*?def \w+\(.*?\):.*?(?=@app\.route|\Z)",
    r"@app\.route\(['\"]/api/wellness/history['\"].*?def \w+\(.*?\):.*?(?=@app\.route|\Z)",
    r"@app\.route\(['\"]/api/glucose/history['\"].*?def \w+\(.*?\):.*?(?=@app\.route|\Z)",
    r"@app\.route\(['\"]/api/health-trends['\"].*?def \w+\(.*?\):.*?(?=@app\.route|\Z)",
    r"@app\.route\(['\"]/api/forecast/predict['\"].*?def \w+\(.*?\):.*?(?=@app\.route|\Z)",
]

for r_pat in routes_to_check:
    match = re.search(r_pat, text, re.DOTALL)
    print("==================================================================")
    if match:
        print(match.group(0)[:1200])
    else:
        print(f"NOT FOUND: {r_pat}")
