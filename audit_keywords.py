import os

keywords = ['142', '150', '100', '49.9', 'DEMO MODE', 'DEMO DATA', 'DEMO PREDICTION', 'Maria Andrade', 'mockActual', 'mockData', '+12 from last', '07:30 today', 'Breakfast', 'Stress 4/10', 'GRU MODEL NOT CONNECTED']
templates_dir = 'templates'

matches = {}
for root, dirs, files in os.walk(templates_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                for kw in keywords:
                    if kw in content:
                        matches.setdefault(f, []).append(kw)

for f, kws in matches.items():
    print(f"{f}: {kws}")
