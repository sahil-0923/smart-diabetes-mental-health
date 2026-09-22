import os

targets = ['201', '133.3', '133.6', '138.7', '145.3', 'demo analysis', 'demo data shown throughout', 'evening spike', 'aug 22', 'spike on']
search_dirs = ['templates', 'ai', 'static']
search_files = ['app.py']

matches = []

for d in search_dirs:
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith(('.html', '.py', '.js', '.css')):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as file_obj:
                    for line_idx, line in enumerate(file_obj, 1):
                        for t in targets:
                            if t in line.lower():
                                matches.append((p, line_idx, t, line.strip()))

for f in search_files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8', errors='ignore') as file_obj:
            for line_idx, line in enumerate(file_obj, 1):
                for t in targets:
                    if t in line.lower():
                        matches.append((f, line_idx, t, line.strip()))

print(f"Total occurrences found: {len(matches)}")
for m in matches:
    print(f"{m[0]}:{m[1]} [{m[2]}] -> {m[3][:120]}")
