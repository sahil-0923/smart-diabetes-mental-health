import requests
import json

BASE_URL = 'http://127.0.0.1:5002'

session1 = requests.Session()
# Login User 1 (from previous tests)
session1.post(f"{BASE_URL}/login", data={'email': 'testuser2@example.com', 'password': 'password123'})

print("--- Testing /api/glucose/history ---")
r = session1.get(f"{BASE_URL}/api/glucose/history?days=7")
print(json.dumps(r.json(), indent=2))

print("\n--- Testing /api/glucose/trend ---")
r = session1.get(f"{BASE_URL}/api/glucose/trend")
print(json.dumps(r.json(), indent=2))

print("\n--- Testing /api/wellness/history ---")
r = session1.get(f"{BASE_URL}/api/wellness/history")
print(json.dumps(r.json(), indent=2))

print("\n--- Testing /api/health-trends ---")
r = session1.get(f"{BASE_URL}/api/health-trends")
print(json.dumps(r.json(), indent=2))

print("\n--- Testing /api/health-records/recent ---")
r = session1.get(f"{BASE_URL}/api/health-records/recent?limit=2")
print(json.dumps(r.json(), indent=2))

print("\n--- Testing /api/health/summary ---")
r = session1.get(f"{BASE_URL}/api/health/summary")
print(json.dumps(r.json(), indent=2))

# Test Empty Data / User Isolation
print("\n--- Testing User Isolation (New User) ---")
session2 = requests.Session()
session2.post(f"{BASE_URL}/register", data={'name': 'Empty User', 'email': 'empty@example.com', 'password': 'password123', 'diabetes_type': 'Type 1'})
session2.post(f"{BASE_URL}/login", data={'email': 'empty@example.com', 'password': 'password123'})

r_empty = session2.get(f"{BASE_URL}/api/glucose/history")
print("Empty User Glucose History:", r_empty.json())

# Test Unauthenticated
print("\n--- Testing Unauthenticated Access ---")
session3 = requests.Session()
r_unauth = session3.get(f"{BASE_URL}/api/glucose/history")
# Should redirect to login or return 401. Since login_required uses redirect, it will be 200 with HTML or 302
print("Unauth status code (redirects to login):", len(r_unauth.text), "bytes of HTML")
