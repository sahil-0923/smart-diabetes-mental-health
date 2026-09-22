import os

targets = []
for root, dirs, files in os.walk("templates"):
    for f in files:
        if f.endswith(".html"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file_obj:
                content = file_obj.read()
                if "topbar" in content or "top-actions" in content or "search-box" in content or "emergency-btn" in content:
                    targets.append(p)

print(f"Templates with topbar elements ({len(targets)}):")
for t in targets:
    print(f"  • {t}")
