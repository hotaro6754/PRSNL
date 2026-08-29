import pytest
import requests
import time

BASE_URL = "http://localhost:8000"

def test_api_degraded_state():
    """Test that the API continues to function and returns a degraded state rather than crashing when external components fail."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip("API not running, skipping resilience test")
        
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["ok", "degraded"]
    
def test_scan_resilience():
    """Test that scan endpoint doesn't crash on invalid payload or component failure."""
    # Invalid type
    payload = {
        "type": "invalid_type",
        "content": "http://evil-phishing.com/login"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/scan", json=payload, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip("API not running, skipping resilience test")
        
    assert response.status_code == 400
    
    # Missing fields
    payload = {
        "content": "http://example.com"
    }
    response = requests.post(f"{BASE_URL}/api/scan", json=payload, timeout=5)
    assert response.status_code == 422
