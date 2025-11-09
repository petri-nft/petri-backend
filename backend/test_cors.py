#!/usr/bin/env python
"""Test to verify CORS configuration works for frontend requests."""
import requests
import json

BACKEND_URL = "http://localhost:8000/api"
FRONTEND_ORIGIN = "http://localhost:8080"

def test_cors_preflight():
    """Test CORS preflight request."""
    print("\n" + "="*80)
    print("TESTING CORS PREFLIGHT REQUEST")
    print("="*80)
    
    headers = {
        "Origin": FRONTEND_ORIGIN,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    }
    
    response = requests.options(f"{BACKEND_URL}/trees", headers=headers)
    
    print(f"\n✓ Preflight Status: {response.status_code}")
    print("\n✓ CORS Headers:")
    for header in [
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Credentials",
        "Access-Control-Max-Age",
    ]:
        value = response.headers.get(header, "NOT SET")
        print(f"  - {header}: {value}")
    
    # Verify required headers
    assert response.headers.get("Access-Control-Allow-Origin"), "Missing Allow-Origin header"
    assert response.status_code == 200, f"Preflight failed with status {response.status_code}"
    
    return True


def test_cors_with_request():
    """Test actual request includes CORS headers."""
    print("\n" + "="*80)
    print("TESTING CORS WITH ACTUAL REQUEST")
    print("="*80)
    
    headers = {
        "Origin": FRONTEND_ORIGIN,
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token",
    }
    
    response = requests.get(f"{BACKEND_URL}/health", headers=headers)
    
    print(f"\n✓ Request Status: {response.status_code}")
    print(f"✓ Response Body: {json.dumps(response.json(), indent=2)}")
    
    print("\n✓ CORS Headers in Response:")
    cors_headers = {
        k: v for k, v in response.headers.items() 
        if k.lower().startswith("access-control")
    }
    for key, value in cors_headers.items():
        print(f"  - {key}: {value}")
    
    assert "Access-Control-Allow-Origin" in response.headers, "Missing Allow-Origin header"
    
    return True


def test_cors_multiple_origins():
    """Test CORS works for different origins."""
    print("\n" + "="*80)
    print("TESTING CORS FOR MULTIPLE ORIGINS")
    print("="*80)
    
    origins = [
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
    ]
    
    for origin in origins:
        headers = {"Origin": origin}
        response = requests.options(f"{BACKEND_URL}/trees", headers=headers)
        
        allow_origin = response.headers.get("Access-Control-Allow-Origin")
        
        # Check if the origin is allowed (either explicitly or via wildcard)
        is_allowed = (allow_origin == origin or allow_origin == "*")
        status = "✓" if is_allowed else "❌"
        
        print(f"{status} {origin}: {allow_origin}")
        
        assert is_allowed, f"Origin {origin} not allowed"
    
    return True


def run_all_tests():
    """Run all CORS tests."""
    print("\n" + "="*80)
    print("CORS CONFIGURATION VERIFICATION")
    print("="*80)
    print(f"Frontend Origin: {FRONTEND_ORIGIN}")
    print(f"Backend URL: {BACKEND_URL}")
    
    try:
        test_cors_preflight()
        test_cors_with_request()
        test_cors_multiple_origins()
        
        print("\n" + "="*80)
        print("✅ ALL CORS TESTS PASSED")
        print("="*80)
        print("\n✅ Frontend can now successfully communicate with backend!")
        print("\nNext Steps:")
        print("  1. Refresh the frontend browser (Ctrl+Shift+R)")
        print("  2. Try planting a tree")
        print("  3. Should work without CORS errors")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
