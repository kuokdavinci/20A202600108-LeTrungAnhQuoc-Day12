import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Login
print("Logging in...")
resp = requests.post(f"{BASE_URL}/auth/token", json={"username": "student", "password": "demo123"})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Test rate limit (10 req/min)
print("\nTesting rate limit (10 requests)...")
for i in range(12):
    r = requests.post(f"{BASE_URL}/ask", json={"question": f"Test {i}"}, headers=headers)
    if r.status_code == 200:
        print(f"Request {i+1}: OK (Remaining: {r.json()['usage']['requests_remaining']})")
    elif r.status_code == 429:
        print(f"Request {i+1}: FAILED (Rate limit exceeded!)")
        break
    else:
        print(f"Request {i+1}: Error {r.status_code} - {r.text}")

# 3. Check usage stats
r = requests.get(f"{BASE_URL}/me/usage", headers=headers)
print(f"\nUsage Stats: {r.json()}")
