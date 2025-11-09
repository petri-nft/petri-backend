"""
Test Script for Plant a Tree Backend API

Run this script to test all major endpoints.
Requires backend server running at http://localhost:8000
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Store tokens for testing
access_token = None
user_id = None
tree_id = None
token_id = None


def print_section(title: str):
    """Print a formatted section title."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_response(response: requests.Response, title: str = "Response"):
    """Print formatted response."""
    print(f"{title}:")
    print(f"Status: {response.status_code}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")
    print()


def set_auth_header():
    """Set authorization header with token."""
    if access_token:
        HEADERS["Authorization"] = f"Bearer {access_token}"


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

def test_register():
    """Test user registration."""
    print_section("1. USER REGISTRATION")
    
    url = f"{BASE_URL}/api/auth/register"
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    print_response(response, "Register User")
    
    if response.status_code == 201:
        global user_id
        user_id = response.json()["id"]
        return True
    elif response.status_code == 400:
        print("User already exists, continuing with login...")
        return True
    return False


def test_login():
    """Test user login."""
    print_section("2. USER LOGIN")
    
    url = f"{BASE_URL}/api/auth/login"
    payload = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    print_response(response, "Login")
    
    if response.status_code == 200:
        global access_token
        access_token = response.json()["access_token"]
        set_auth_header()
        print(f"✓ Login successful, token obtained")
        return True
    return False


# =============================================================================
# TREE TESTS
# =============================================================================

def test_plant_tree():
    """Test planting a tree."""
    print_section("3. PLANT A TREE")
    
    set_auth_header()
    url = f"{BASE_URL}/api/trees"
    payload = {
        "species": "oak",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "location_name": "Central Park, NYC",
        "description": "Test oak tree"
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    print_response(response, "Plant Tree")
    
    if response.status_code == 201:
        global tree_id
        tree_id = response.json()["id"]
        print(f"✓ Tree planted successfully, ID: {tree_id}")
        return True
    return False


def test_get_tree():
    """Test getting tree details."""
    print_section("4. GET TREE DETAILS")
    
    set_auth_header()
    if not tree_id:
        print("⚠ Tree ID not available, skipping...")
        return False
    
    url = f"{BASE_URL}/api/trees/{tree_id}"
    response = requests.get(url, headers=HEADERS)
    print_response(response, "Get Tree")
    
    return response.status_code == 200


def test_list_trees():
    """Test listing trees."""
    print_section("5. LIST USER'S TREES")
    
    set_auth_header()
    url = f"{BASE_URL}/api/trees"
    response = requests.get(url, headers=HEADERS)
    print_response(response, "List Trees")
    
    return response.status_code == 200


def test_update_health():
    """Test updating tree health."""
    print_section("6. UPDATE TREE HEALTH")
    
    set_auth_header()
    if not tree_id:
        print("⚠ Tree ID not available, skipping...")
        return False
    
    url = f"{BASE_URL}/api/trees/{tree_id}/updateHealth"
    payload = {
        "health_score": 95.5,
        "event_type": "growth",
        "description": "Tree is growing well"
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    print_response(response, "Update Health")
    
    return response.status_code == 200


def test_get_health_history():
    """Test getting health history."""
    print_section("7. GET HEALTH HISTORY")
    
    set_auth_header()
    if not tree_id:
        print("⚠ Tree ID not available, skipping...")
        return False
    
    url = f"{BASE_URL}/api/trees/{tree_id}/health-history"
    response = requests.get(url, headers=HEADERS)
    print_response(response, "Get Health History")
    
    return response.status_code == 200


# =============================================================================
# TOKEN TESTS
# =============================================================================

def test_mint_token():
    """Test minting an NFT token."""
    print_section("8. MINT TOKEN")
    
    set_auth_header()
    if not tree_id:
        print("⚠ Tree ID not available, skipping...")
        return False
    
    url = f"{BASE_URL}/api/trees/{tree_id}/mint"
    response = requests.post(url, headers=HEADERS)
    print_response(response, "Mint Token")
    
    if response.status_code == 200:
        global token_id
        token_id = response.json()["token_id"]
        print(f"✓ Token minted successfully, ID: {token_id}")
        return True
    elif response.status_code == 400:
        print("Token already minted for this tree, continuing...")
        return True
    return False


def test_get_token():
    """Test getting token details."""
    print_section("9. GET TOKEN DETAILS")
    
    set_auth_header()
    if not token_id:
        print("⚠ Token ID not available, skipping...")
        return False
    
    url = f"{BASE_URL}/api/tokens/{token_id}"
    response = requests.get(url, headers=HEADERS)
    print_response(response, "Get Token")
    
    return response.status_code == 200


def test_list_tokens():
    """Test listing tokens."""
    print_section("10. LIST USER'S TOKENS")
    
    set_auth_header()
    url = f"{BASE_URL}/api/tokens"
    response = requests.get(url, headers=HEADERS)
    print_response(response, "List Tokens")
    
    return response.status_code == 200


# =============================================================================
# TRADING TESTS
# =============================================================================

def test_create_trade():
    """Test creating a trade."""
    print_section("11. CREATE TRADE")
    
    set_auth_header()
    if not token_id:
        print("⚠ Token ID not available, skipping...")
        return False
    
    url = f"{BASE_URL}/api/tokens/{token_id}/trade"
    payload = {
        "trade_type": "buy",
        "quantity": 10.0,
        "price_per_unit": 95.0
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    print_response(response, "Create Trade")
    
    return response.status_code == 201


def test_get_trades():
    """Test getting trades."""
    print_section("12. GET TOKEN TRADES")
    
    set_auth_header()
    if not token_id:
        print("⚠ Token ID not available, skipping...")
        return False
    
    url = f"{BASE_URL}/api/tokens/{token_id}/trades"
    response = requests.get(url, headers=HEADERS)
    print_response(response, "Get Trades")
    
    return response.status_code == 200


# =============================================================================
# PORTFOLIO TESTS
# =============================================================================

def test_get_portfolio():
    """Test getting portfolio."""
    print_section("13. GET PORTFOLIO")
    
    set_auth_header()
    url = f"{BASE_URL}/api/portfolio/me"
    response = requests.get(url, headers=HEADERS)
    print_response(response, "Get Portfolio")
    
    return response.status_code == 200


# =============================================================================
# HEALTH CHECK
# =============================================================================

def test_health():
    """Test health endpoint."""
    print_section("HEALTH CHECK")
    
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print_response(response, "Health Check")
    
    return response.status_code == 200


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║  Plant a Tree Backend - API Test Suite              ║")
    print("║  Make sure the backend server is running!           ║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Health Check", test_health),
        ("Register User", test_register),
        ("Login User", test_login),
        ("Plant Tree", test_plant_tree),
        ("Get Tree", test_get_tree),
        ("List Trees", test_list_trees),
        ("Update Health", test_update_health),
        ("Get Health History", test_get_health_history),
        ("Mint Token", test_mint_token),
        ("Get Token", test_get_token),
        ("List Tokens", test_list_tokens),
        ("Create Trade", test_create_trade),
        ("Get Trades", test_get_trades),
        ("Get Portfolio", test_get_portfolio),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "✓ PASS" if result else "✗ FAIL"))
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            results.append((test_name, f"✗ ERROR: {str(e)}"))
    
    # Print summary
    print_section("TEST SUMMARY")
    for test_name, result in results:
        print(f"{test_name:.<40} {result}")
    
    passed = sum(1 for _, result in results if "PASS" in result)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
