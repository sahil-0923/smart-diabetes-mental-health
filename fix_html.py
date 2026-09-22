import re

with open('templates/monitoring.html', 'r', encoding='utf-8') as f:
    content = f.read()

hidden_inputs = """
    <input type="hidden" name="meal_context" id="meal_context_input" value="Fasting">
    <div style="margin-top:20px; display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
        <div>
            <label class="stat-label" style="display:block; margin-bottom:8px;">Stress (0-10)</label>
            <input type="number" name="stress" class="input-std" min="0" max="10" placeholder="e.g. 5">
        </div>
        <div>
            <label class="stat-label" style="display:block; margin-bottom:8px;">Sleep (hours)</label>
            <input type="number" name="sleep" class="input-std" step="0.1" placeholder="e.g. 7.5">
        </div>
        <div>
            <label class="stat-label" style="display:block; margin-bottom:8px;">Steps</label>
            <input type="number" name="steps" class="input-std" placeholder="e.g. 8000">
        </div>
        <div>
            <label class="stat-label" style="display:block; margin-bottom:8px;">Weight (kg)</label>
            <input type="number" name="weight" class="input-std" step="0.1" placeholder="e.g. 70.5">
        </div>
        <div>
            <label class="stat-label" style="display:block; margin-bottom:8px;">Mood (1-10)</label>
            <input type="number" name="mood" class="input-std" min="1" max="10" placeholder="e.g. 8">
        </div>
        <div>
            <label class="stat-label" style="display:block; margin-bottom:8px;">Exercise Duration (min)</label>
            <input type="number" name="exercise_duration" class="input-std" placeholder="e.g. 30">
        </div>
    </div>
"""

content = content.replace('</form>', hidden_inputs + '\n</form>')

js_replacement = """
        document.querySelectorAll('.radio-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.radio-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                document.getElementById('meal_context_input').value = card.querySelector('.radio-title').innerText;
            });
        });
"""
content = re.sub(r'document\.querySelectorAll\(\'\.radio-card\'\)\.forEach\(card => \{.*?\}\);', js_replacement, content, flags=re.DOTALL)

with open('templates/monitoring.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated monitoring.html')
