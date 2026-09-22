import re
import os

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith('@app.route("/")') or line.startswith("@app.route('/')"):
        new_lines.append("@app.route('/')\n")
        new_lines.append("def index():\n")
        new_lines.append("    return render_template('landing.html')\n")
        skip = True
        continue
    
    if skip:
        # We need to know when to stop skipping. We skip until the next route
        if line.startswith('@app.route'):
            skip = False
            new_lines.append(line)
        continue
        
    if not skip:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Fixed root route in app.py")
