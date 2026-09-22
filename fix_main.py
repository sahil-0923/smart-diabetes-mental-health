import re
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the exact main block. We know it starts around 4265.
# We'll just split on `if __name__ == "__main__":`
if 'if __name__ == "__main__":' in text:
    parts = text.split('if __name__ == "__main__":')
    # The first part is everything before.
    # The second part is the block PLUS the onboarding routes that were appended.
    # Wait, the onboarding routes were appended to the end of the file.
    
    # We want to extract JUST the main block.
    # Let's find where the onboarding routes start. They start with `@app.route('/onboarding` or similar.
    # Let's search for the first `@app.route` after the main block.
    
    main_and_after = parts[1]
    
    # The main block ends when we encounter a new @app.route (or just move the whole main block manually)
    # Let's manually parse app.py and move lines
    pass

# Better approach:
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

main_idx = -1
for i, line in enumerate(lines):
    if 'if __name__ == "__main__":' in line:
        main_idx = i
        break

if main_idx != -1:
    # Find the end of the main block. It ends where the indentation goes back to 0.
    end_idx = main_idx + 1
    while end_idx < len(lines) and (lines[end_idx].startswith(' ') or lines[end_idx].strip() == ''):
        end_idx += 1
        
    main_block = lines[main_idx:end_idx]
    
    # Remove main block
    new_lines = lines[:main_idx] + lines[end_idx:]
    
    # Add main block to the end
    new_lines.extend(['\n\n'] + main_block)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Main block moved successfully.")
else:
    print("Main block not found.")
