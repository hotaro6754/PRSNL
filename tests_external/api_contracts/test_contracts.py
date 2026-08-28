import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_api_health():
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("API not running")
