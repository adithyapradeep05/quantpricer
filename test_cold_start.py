#!/usr/bin/env python3
"""
Quick test script to verify cold-start handling system
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/health")
    duration = time.time() - start
    
    print(f"Response: {response.json()}")
    print(f"Duration: {duration:.3f}s")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert duration < 0.1  # Should be very fast
    print("Health check passed\n")

def test_price_endpoint():
    """Test price endpoint with idempotency"""
    print("Testing /price endpoint...")
    
    payload = {
        "S": 100,
        "K": 100,
        "r": 0.05,
        "sigma": 0.2,
        "T": 1.0,
        "type": "call",
        "idempotencyKey": "test-123"
    }
    
    # First request
    response1 = requests.post(f"{BASE_URL}/price", json=payload)
    print(f"First request status: {response1.status_code}")
    result1 = response1.json()
    print(f"First result: {json.dumps(result1, indent=2)}")
    
    # Second request with same key (should be identical)
    response2 = requests.post(f"{BASE_URL}/price", json=payload)
    print(f"Second request status: {response2.status_code}")
    result2 = response2.json()
    print(f"Second result: {json.dumps(result2, indent=2)}")
    
    # Third request with different key
    payload["idempotencyKey"] = "test-456"
    response3 = requests.post(f"{BASE_URL}/price", json=payload)
    print(f"Third request status: {response3.status_code}")
    result3 = response3.json()
    print(f"Third result: {json.dumps(result3, indent=2)}")
    
    # Verify idempotency
    assert result1 == result2, "Idempotency failed - same key should return same result"
    assert result1 != result3, "Different keys should return different results"
    
    # Verify response structure
    assert "price" in result1
    assert "greeks" in result1
    assert "meta" in result1
    assert result1["meta"]["engine"] == "lazy-bs"
    
    print("Price endpoint with idempotency passed\n")

def test_error_handling():
    """Test error handling"""
    print("Testing error handling...")
    
    # Invalid inputs
    invalid_payload = {
        "S": -100,  # Invalid negative price
        "K": 100,
        "r": 0.05,
        "sigma": 0.2,
        "T": 1.0,
        "type": "call"
    }
    
    response = requests.post(f"{BASE_URL}/price", json=invalid_payload)
    print(f"Invalid input response: {response.status_code}")
    print(f"Error message: {response.json()}")
    
    assert response.status_code == 400
    print("Error handling passed\n")

def main():
    print("Testing QuantPricer Cold-Start System\n")
    
    try:
        test_health()
        test_price_endpoint()
        test_error_handling()
        print("All tests passed! Cold-start system is working correctly.")
    except Exception as e:
        print(f"Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
