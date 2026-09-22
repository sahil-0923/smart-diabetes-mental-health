import re
import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add fields to class User
user_fields = """
    profile_completed = db.Column(db.Boolean, default=False)
    onboarding_completed = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    diabetes_type = db.Column(db.String(50))
    years_since_diagnosis = db.Column(db.Integer)
    hba1c = db.Column(db.Float)
    current_medication = db.Column(db.String(255))
    blood_pressure = db.Column(db.String(50))
    cholesterol = db.Column(db.Float)
    smoking_status = db.Column(db.String(50))
    activity_level = db.Column(db.String(50))
    typical_sleep = db.Column(db.Float)
    typical_stress = db.Column(db.Integer)
"""

if 'profile_completed = db.Column' not in content:
    content = content.replace(
        'created_at = db.Column(\n        db.DateTime,\n        default=datetime.utcnow\n    )',
        'created_at = db.Column(\n        db.DateTime,\n        default=datetime.utcnow\n    )' + user_fields
    )

# 2. Add onboarding_required decorator
decorator_code = """
from functools import wraps

def onboarding_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('login'))
        if not user.profile_completed:
            return redirect(url_for('onboarding_profile'))
        if not user.onboarding_completed:
            return redirect(url_for('onboarding_history'))
        return f(*args, **kwargs)
    return decorated_function
"""
if 'def onboarding_required(f):' not in content:
    content = content.replace('def get_current_user():', decorator_code + '\n\ndef get_current_user():')


# 3. Apply onboarding_required to dashboard, monitoring, glucose, mental_wellness, health_trends, etc.
routes_to_protect = [
    'def dashboard():',
    'def monitoring():',
    'def glucose():',
    'def mental_wellness():',
    'def health_trends():',
    'def nutrition():',
    'def workouts():',
    'def ai_forecast():',
    'def risk_trends():',
    'def simulator():'
]

for route in routes_to_protect:
    if f'@onboarding_required\ndef {route[4:-2]}' not in content:
        content = content.replace(
            f'@login_required\n{route}',
            f'@login_required\n@onboarding_required\n{route}'
        )

# 4. Modify root route
root_route_new = """@app.route('/')
def index():
    return render_template('landing.html')"""
content = re.sub(r"@app\.route\('/'\)[\s\S]*?def index\(\):[\s\S]*?return redirect\(url_for\('login'\)\)", root_route_new, content)


# 5. Add Onboarding Routes
onboarding_routes = """
@app.route('/onboarding/profile', methods=['GET', 'POST'])
@login_required
def onboarding_profile():
    user = get_current_user()
    if request.method == 'POST':
        user.age = int(request.form.get('age')) if request.form.get('age') else None
        user.gender = request.form.get('gender')
        user.height = float(request.form.get('height')) if request.form.get('height') else None
        user.weight = float(request.form.get('weight')) if request.form.get('weight') else None
        user.diabetes_type = request.form.get('diabetes_type')
        user.years_since_diagnosis = int(request.form.get('years_since_diagnosis')) if request.form.get('years_since_diagnosis') else None
        user.hba1c = float(request.form.get('hba1c')) if request.form.get('hba1c') else None
        user.current_medication = request.form.get('current_medication')
        user.blood_pressure = request.form.get('blood_pressure')
        user.cholesterol = float(request.form.get('cholesterol')) if request.form.get('cholesterol') else None
        user.smoking_status = request.form.get('smoking_status')
        user.activity_level = request.form.get('activity_level')
        user.typical_sleep = float(request.form.get('typical_sleep')) if request.form.get('typical_sleep') else None
        user.typical_stress = int(request.form.get('typical_stress')) if request.form.get('typical_stress') else None
        
        user.profile_completed = True
        db.session.commit()
        return redirect(url_for('onboarding_history'))
        
    return render_template('onboarding_profile.html', user=user)

@app.route('/onboarding/history', methods=['GET', 'POST'])
@login_required
def onboarding_history():
    user = get_current_user()
    if not user.profile_completed:
        return redirect(url_for('onboarding_profile'))
        
    if request.method == 'POST':
        # Simple array processing for 7 days
        dates = request.form.getlist('date[]')
        glucoses = request.form.getlist('glucose[]')
        stresses = request.form.getlist('stress[]')
        sleeps = request.form.getlist('sleep[]')
        steps_list = request.form.getlist('steps[]')
        weights = request.form.getlist('weight[]')
        moods = request.form.getlist('mood[]')
        meals = request.form.getlist('meal_context[]')
        exercises = request.form.getlist('exercise_duration[]')
        
        from datetime import datetime
        for i in range(len(dates)):
            if not dates[i] or not glucoses[i]: continue
            
            try:
                ts = datetime.strptime(dates[i], '%Y-%m-%dT%H:%M')
            except ValueError:
                ts = datetime.now()
                
            hr = HealthRecord(
                user_id=user.id,
                date=dates[i][:10], # Keep legacy string format compatibility if needed
                glucose=float(glucoses[i]) if glucoses[i] else 0.0,
                stress=float(stresses[i]) if stresses[i] else 0.0,
                sleep=float(sleeps[i]) if sleeps[i] else 0.0,
                steps=int(steps_list[i]) if steps_list[i] else 0,
                weight=float(weights[i]) if weights[i] else 0.0,
                mood=moods[i] if moods[i] else '5',
                meal_context=meals[i] if meals[i] else 'Random',
                exercise_duration=float(exercises[i]) if exercises[i] else 0.0
            )
            # Actually we want proper timestamp
            hr.timestamp = ts
            db.session.add(hr)
            
        user.onboarding_completed = True
        db.session.commit()
        return redirect(url_for('onboarding_review'))
        
    return render_template('onboarding_history.html', user=user)

@app.route('/onboarding/review')
@login_required
def onboarding_review():
    user = get_current_user()
    records_count = HealthRecord.query.filter_by(user_id=user.id).count()
    return render_template('onboarding_review.html', user=user, records_count=records_count)

@app.route('/onboarding/processing')
@login_required
def onboarding_processing():
    return render_template('onboarding_processing.html')
"""

if '@app.route(\'/onboarding/profile\'' not in content:
    content += "\n" + onboarding_routes

# 6. Also redirect /login or /register safely? 
# The existing /login already returns redirect(url_for('dashboard')). 
# With @onboarding_required on dashboard, it will auto-redirect them if they aren't onboarded.

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("app.py patched!")
