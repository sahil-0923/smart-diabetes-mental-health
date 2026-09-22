with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

keywords = ['142', 'DEMO MODE', 'DEMO DATA', 'Maria Andrade', 'mockActual', '+12 from last', '07:30 today', 'Breakfast', 'Stress 4/10', 'GRU MODEL NOT CONNECTED']

for i, line in enumerate(lines):
    for kw in keywords:
        if kw in line:
            print(f"Line {i+1}: ({kw}) -> {line.strip()[:100]}")
