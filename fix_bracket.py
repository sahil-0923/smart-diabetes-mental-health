with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('    return redirect(url_for("dashboard"))\n    )\n', '    return redirect(url_for("dashboard"))\n')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed syntax error')
