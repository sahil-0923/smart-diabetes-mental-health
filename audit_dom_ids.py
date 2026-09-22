with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

# Find all id="..." in dashboard.html
ids = re.findall(r'id=["\']([^"\']+)["\']', text)
print("ALL ELEMENT IDs IN dashboard.html:")
for el_id in sorted(set(ids)):
    print(f"  - {el_id}")

# Find all getElementById in dashboard.html
js_ids = re.findall(r'getElementById\(["\']([^"\']+)["\']\)', text)
print("\nALL getElementById IN JS:")
for js_id in sorted(set(js_ids)):
    matched = "EXISTS in HTML" if js_id in ids else "MISSING in HTML!!!"
    print(f"  - {js_id} -> {matched}")
