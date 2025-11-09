#!/usr/bin/env python
"""Debug test to check what headers are being sent."""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Register and login first
register_data = {
    "username": "debuguser",
    "email": "debug@example.com",
    "password": "debug123"
}

print("Registering...")
try:
    resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
except:
    pass  # User may already exist

login_data = {
    "username": register_data["username"],
    "password": register_data["password"]
}

print("Logging in...")
login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
token = login_response.json()["access_token"]
print(f"Token: {token[:30]}...")

# Now test with detailed header inspection
tree_data = {
    "species": "oak",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "location_name": "Test",
    "description": "Test tree"
}

print("\n" + "="*80)
print("Testing with Authorization header")
print("="*80)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print(f"Headers sent: {headers}")

response = requests.post(
    f"{BASE_URL}/trees",
    json=tree_data,
    headers=headers
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Check if it's a header parsing issue by testing with lowercase
print("\n" + "="*80)
print("Testing with lowercase 'authorization' header")
print("="*80)

headers_lower = {
    "authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print(f"Headers sent: {headers_lower}")

response2 = requests.post(
    f"{BASE_URL}/trees",
    json=tree_data,
    headers=headers_lower
)

print(f"Status Code: {response2.status_code}")
print(f"Response: {json.dumps(response2.json(), indent=2)}")
