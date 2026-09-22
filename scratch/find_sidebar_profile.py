import os

found = []
for root, dirs, files in os.walk("templates"):
    for f in files:
        if f.endswith(".html"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file_obj:
                for idx, line in enumerate(file_obj, 1):
                    if "user-profile-sidebar" in line or "logout-btn" in line or ">MA<" in line:
                        found.append((p, idx, line.strip()))

print(f"Found {len(found)} references:")
for p, idx, l in found:
    print(f"  {p}:{idx} -> {l[:100]}")
