import requests
import json

s = requests.Session()

# 1. Login
data = {'email': 'test@example.com', 'password': 'password'}
res = s.post('http://127.0.0.1:5050/login', data=data)
print("Login status:", res.status_code)

# 2. Test APIs
endpoints = [
    '/api/health/summary',
    '/api/health-records/recent',
    '/api/glucose/history?days=7',
    '/api/glucose/trend',
    '/api/wellness/history?days=7',
    '/api/health-trends?days=7'
]

for ep in endpoints:
    url = f'http://127.0.0.1:5050{ep}'
    r = s.get(url)
    print(f"\n--- GET {ep} ---")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text)
