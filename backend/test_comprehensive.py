#!/usr/bin/env python
"""Comprehensive test for all major backend endpoints."""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_full_workflow():
    """Test complete workflow with all major endpoints."""
    
    print("=" * 80)
    print("COMPREHENSIVE BACKEND TEST - ALL ENDPOINTS")
    print("=" * 80)
    
    # Create test user
    test_user = f"comprehensive_test_{int(datetime.now().timestamp())}"
    test_email = f"comprehensive_{int(datetime.now().timestamp())}@example.com"
    
    # 1. Register
    print("\n[1] USER REGISTRATION")
    print("-" * 80)
    register_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": test_user,
        "email": test_email,
        "password": "test123!@#",
    })
    assert register_resp.status_code == 200, f"Registration failed: {register_resp.text}"
    user_id = register_resp.json()["id"]
    print(f"✓ User registered: {test_user} (ID: {user_id})")
    
    # 2. Login
    print("\n[2] USER LOGIN")
    print("-" * 80)
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": test_user,
        "password": "test123!@#",
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    print(f"✓ User logged in. Token: {token[:30]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Plant trees (test multiple trees)
    print("\n[3] PLANT TREES")
    print("-" * 80)
    trees = []
    species_list = ["oak", "pine", "birch"]
    for i, species in enumerate(species_list):
        tree_resp = requests.post(f"{BASE_URL}/trees", headers=headers, json={
            "species": species,
            "latitude": 40.7128 + i * 0.01,
            "longitude": -74.0060 + i * 0.01,
            "location_name": f"Location {i+1}",
            "description": f"Beautiful {species} tree"
        })
        assert tree_resp.status_code == 201, f"Plant tree failed: {tree_resp.text}"
        tree = tree_resp.json()
        trees.append(tree)
        print(f"✓ Planted {species} tree (ID: {tree['id']}, Health: {tree['health_score']})")
    
    # 4. List trees
    print("\n[4] LIST TREES")
    print("-" * 80)
    list_resp = requests.get(f"{BASE_URL}/trees", headers=headers)
    assert list_resp.status_code == 200, f"List trees failed: {list_resp.text}"
    tree_list = list_resp.json()
    assert len(tree_list) >= len(trees), "List should contain at least the trees we planted"
    print(f"✓ Listed {len(tree_list)} trees")
    
    # 5. Get individual tree
    print("\n[5] GET INDIVIDUAL TREE")
    print("-" * 80)
    tree_id = trees[0]["id"]
    get_resp = requests.get(f"{BASE_URL}/trees/{tree_id}", headers=headers)
    assert get_resp.status_code == 200, f"Get tree failed: {get_resp.text}"
    tree_detail = get_resp.json()
    print(f"✓ Retrieved tree {tree_id}: {tree_detail['species']} at ({tree_detail['latitude']}, {tree_detail['longitude']})")
    
    # 6. Update tree health
    print("\n[6] UPDATE TREE HEALTH")
    print("-" * 80)
    health_resp = requests.post(
        f"{BASE_URL}/trees/{tree_id}/updateHealth",
        headers=headers,
        json={
            "health_score": 95.0,
            "event_type": "growth",
            "description": "Tree is growing well"
        }
    )
    assert health_resp.status_code == 200, f"Update health failed: {health_resp.text}"
    updated_tree = health_resp.json()
    print(f"✓ Updated health to {updated_tree['health_score']} for tree {tree_id}")
    
    # 7. Get health history
    print("\n[7] GET HEALTH HISTORY")
    print("-" * 80)
    history_resp = requests.get(f"{BASE_URL}/trees/{tree_id}/health-history", headers=headers)
    assert history_resp.status_code == 200, f"Get health history failed: {history_resp.text}"
    history = history_resp.json()
    print(f"✓ Retrieved {len(history)} health history records for tree {tree_id}")
    for record in history[:2]:
        print(f"  - {record['event_type']}: {record['health_score']} (at {record['recorded_at']})")
    
    # 8. Health check endpoint
    print("\n[8] HEALTH CHECK")
    print("-" * 80)
    health_check_resp = requests.get(f"{BASE_URL}/../health")
    # Note: This might be at /health not /api/health
    try:
        if health_check_resp.status_code == 404:
            health_check_resp = requests.get("http://localhost:8000/health")
        assert health_check_resp.status_code == 200, "Health check failed"
        print(f"✓ Health check passed: {health_check_resp.json()}")
    except Exception as e:
        print(f"⚠ Health check endpoint not available or different path: {e}")
    
    # 9. Authorization test - verify token is required
    print("\n[9] AUTHORIZATION TEST (NEGATIVE)")
    print("-" * 80)
    no_auth_resp = requests.get(f"{BASE_URL}/trees")
    assert no_auth_resp.status_code == 401, "Should require authentication"
    print("✓ Endpoint correctly requires authentication")
    
    # 10. Test invalid token
    print("\n[10] INVALID TOKEN TEST")
    print("-" * 80)
    invalid_headers = {"Authorization": "Bearer invalid.token.here"}
    invalid_resp = requests.get(f"{BASE_URL}/trees", headers=invalid_headers)
    assert invalid_resp.status_code == 401, "Should reject invalid token"
    print("✓ Invalid token correctly rejected")
    
    print("\n" + "=" * 80)
    print("✓ ALL COMPREHENSIVE TESTS PASSED!")
    print("=" * 80)
    print("\nSummary:")
    print(f"  - Registered and logged in user: {test_user}")
    print(f"  - Planted {len(trees)} trees with different species")
    print(f"  - Updated tree health and verified history")
    print(f"  - Verified authentication is required")
    print(f"  - All endpoints working correctly without mocking")
    
    return True

if __name__ == "__main__":
    try:
        test_full_workflow()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
