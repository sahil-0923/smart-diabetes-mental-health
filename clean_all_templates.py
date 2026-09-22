import glob

templates = glob.glob("templates/*.html")

for tpath in templates:
    with open(tpath, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False
    if "DEMO MODE — AI predictions are not medical advice" in content:
        content = content.replace("DEMO MODE — AI predictions are not medical advice", "RESEARCH PROTOTYPE — AI forecasts are informational and not medical advice.")
        modified = True
    if "<div class=\"top-avatar\">MA</div>" in content:
        content = content.replace("<div class=\"top-avatar\">MA</div>", "<div class=\"top-avatar\">{{ user.name[:2].upper() if user and user.name else 'PT' }}</div>")
        modified = True
    if "Maria Andrade" in content and "user.name" in content:
        content = content.replace("'Maria Andrade'", "'Patient'")
        modified = True

    if modified:
        with open(tpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned {tpath}")
