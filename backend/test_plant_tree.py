#!/usr/bin/env python
"""Test script for plant tree functionality."""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_plant_tree_flow():
    """Test the complete flow of planting a tree."""
    
    print("=" * 80)
    print("TESTING PLANT TREE FUNCTIONALITY")
    print("=" * 80)
    
    # Step 1: Register a user
    print("\n[1] Registering a test user...")
    register_data = {
        "username": f"testuser_{int(datetime.now().timestamp())}",
        "email": f"testuser_{int(datetime.now().timestamp())}@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("❌ Registration failed!")
            return False
        
        user_id = response.json().get("id")
        print(f"✓ User registered with ID: {user_id}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Step 2: Login user
    print("\n[2] Logging in user...")
    login_data = {
        "username": register_data["username"],
        "password": register_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("❌ Login failed!")
            return False
        
        token = response.json().get("access_token")
        print(f"✓ User logged in. Token: {token[:20]}...")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 3: Plant a tree
    print("\n[3] Planting a tree...")
    tree_data = {
        "species": "oak",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "location_name": "New York City",
        "description": "A beautiful oak tree in NYC"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/trees",
            json=tree_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 201:
            print("❌ Tree planting failed!")
            print(f"Error details: {response.text}")
            return False
        
        tree_id = response.json().get("id")
        print(f"✓ Tree planted successfully with ID: {tree_id}")
    except Exception as e:
        print(f"❌ Tree planting error: {e}")
        return False
    
    # Step 4: Get the tree
    print("\n[4] Retrieving planted tree...")
    try:
        response = requests.get(
            f"{BASE_URL}/trees/{tree_id}",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("❌ Tree retrieval failed!")
            return False
        
        print("✓ Tree retrieved successfully")
    except Exception as e:
        print(f"❌ Tree retrieval error: {e}")
        return False
    
    # Step 5: List all trees
    print("\n[5] Listing all user trees...")
    try:
        response = requests.get(
            f"{BASE_URL}/trees",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("❌ Tree listing failed!")
            return False
        
        trees = response.json()
        print(f"✓ Retrieved {len(trees)} trees")
    except Exception as e:
        print(f"❌ Tree listing error: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_plant_tree_flow()
    sys.exit(0 if success else 1)
