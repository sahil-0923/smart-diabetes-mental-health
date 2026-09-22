import os
import glob
import re

for filepath in glob.glob('templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix Jinja syntax for user profile in the sidebar
    content = content.replace("{ user.name if user else 'Maria Andrade' }", "{{ user.name if user else 'Maria Andrade' }}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed Jinja templates in all files")
