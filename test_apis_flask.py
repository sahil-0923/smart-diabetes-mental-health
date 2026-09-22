from app import app, db, User
import json

app.config['TESTING'] = True
client = app.test_client()

with app.app_context():
    # Login as testuser
    with client.session_transaction() as sess:
        user = User.query.filter_by(email='testuser@example.com').first()
        sess['user_id'] = user.id

    endpoints = [
        '/api/health/summary',
        '/api/health-records/recent?limit=5',
        '/api/glucose/history?days=7',
        '/api/glucose/trend',
        '/api/wellness/history?days=7',
        '/api/health-trends?days=7'
    ]

    for ep in endpoints:
        print(f"\n--- GET {ep} ---")
        res = client.get(ep)
        print("Status:", res.status_code)
        if res.status_code == 200:
            print(json.dumps(res.get_json(), indent=2))
        else:
            print("Failed")
