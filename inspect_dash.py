import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'<div class="card-title">.*?</div>.*?<div class="card-value[^>]*>.*?</div>', text, re.DOTALL):
    print("MATCH:\n", m.group(0))
