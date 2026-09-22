from app import app, db, User, HealthRecord
import json
from datetime import datetime

app.config['TESTING'] = True
client = app.test_client()

with app.app_context():
    # Delete old test users if they exist
    User.query.filter_by(email='newuser@example.com').delete()
    db.session.commit()
    
    # Register new user
    res = client.post('/register', data={'name': 'New Guy', 'email': 'newuser@example.com', 'password': 'password'})
    print("Register Status:", res.status_code)
    
    # Get user
    user = User.query.filter_by(email='newuser@example.com').first()
    print("New user created:", user.id)
    
    # Try accessing dashboard (should redirect to onboarding_profile)
    with client.session_transaction() as sess:
        sess['user_id'] = user.id
        
    res = client.get('/dashboard')
    print("Dashboard GET status (expected 302 to profile):", res.status_code, res.headers.get('Location'))
    
    # Submit profile
    res = client.post('/onboarding/profile', data={
        'age': '30',
        'gender': 'Male',
        'height': '175',
        'weight': '70',
        'diabetes_type': 'Type 1',
        'years_since_diagnosis': '5'
    })
    print("Profile POST status (expected 302 to history):", res.status_code, res.headers.get('Location'))
    
    user = User.query.filter_by(email='newuser@example.com').first()
    print("Profile completed flag:", user.profile_completed)
    
    # Try accessing dashboard (should redirect to onboarding_history)
    res = client.get('/dashboard')
    print("Dashboard GET status (expected 302 to history):", res.status_code, res.headers.get('Location'))
    
    # Submit history
    res = client.post('/onboarding/history', data={
        'date[]': ['2026-08-20T10:00', '2026-08-21T10:00'],
        'glucose[]': ['120', '130'],
        'stress[]': ['5', '6'],
        'sleep[]': ['7', '8'],
        'steps[]': ['5000', '6000'],
        'weight[]': ['70', '70'],
        'mood[]': ['5', '6'],
        'meal_context[]': ['Random', 'Random'],
        'exercise_duration[]': ['30', '40']
    })
    print("History POST status (expected 302 to review):", res.status_code, res.headers.get('Location'))
    
    user = User.query.filter_by(email='newuser@example.com').first()
    print("Onboarding completed flag:", user.onboarding_completed)
    
    # Access dashboard
    res = client.get('/dashboard')
    print("Dashboard GET status (expected 200):", res.status_code)
    
    # Check returning user (testuser)
    user2 = User.query.filter_by(email='testuser@example.com').first()
    with client.session_transaction() as sess:
        sess['user_id'] = user2.id
    res = client.get('/dashboard')
    print("Returning user GET dashboard (expected 302 to profile because existing users have flag=False):", res.status_code, res.headers.get('Location'))
