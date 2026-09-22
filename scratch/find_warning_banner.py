import os

target = "RESEARCH PROTOTYPE"
found = []

for root, dirs, files in os.walk("templates"):
    for f in files:
        if f.endswith(".html"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file_obj:
                for idx, line in enumerate(file_obj, 1):
                    if target.lower() in line.lower() or "top-demo-warning" in line.lower():
                        found.append((p, idx, line.strip()))

print(f"Found {len(found)} occurrences:")
for p, idx, line in found:
    print(f"{p}:{idx} -> {line[:120]}")
