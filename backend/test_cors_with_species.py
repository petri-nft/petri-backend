"""Test CORS headers with species validation error."""
import requests
import json
from app.auth import create_access_token

BASE_URL = "http://localhost:8000/api"

# Create a valid token for user 1
token = create_access_token(data={"sub": "1"})
print(f"Using token: {token[:50]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Origin": "http://localhost:8080"
}

# Test 1: Valid tree creation
print("\n" + "="*60)
print("TEST 1: Valid tree creation with correct species")
print("="*60)
response = requests.post(
    f"{BASE_URL}/trees",
    json={
        "species": "oak",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "location_name": "New York"
    },
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print(f"CORS Headers:")
print(f"  Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT PRESENT')}")
print(f"  Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials', 'NOT PRESENT')}")

# Test 2: Invalid species (should give validation error with CORS headers)
print("\n" + "="*60)
print("TEST 2: Invalid species - should show validation error")
print("="*60)
response = requests.post(
    f"{BASE_URL}/trees",
    json={
        "species": "white_oak",
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print(f"CORS Headers:")
print(f"  Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT PRESENT')}")
print(f"  Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials', 'NOT PRESENT')}")

# Test 3: Test all valid species
print("\n" + "="*60)
print("TEST 3: All valid species")
print("="*60)
valid_species = ["oak", "pine", "birch", "maple", "elm", "spruce"]
for species in valid_species:
    response = requests.post(
        f"{BASE_URL}/trees",
        json={
            "species": species,
            "latitude": 40.7128 + (valid_species.index(species) * 0.1),
            "longitude": -74.0060,
        },
        headers=headers
    )
    status_text = "✅ Created" if response.status_code == 201 else f"❌ {response.status_code}"
    print(f"  {species:10} → {status_text}")

print("\n✅ All tests completed!")
