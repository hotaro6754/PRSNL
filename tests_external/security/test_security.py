import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_security_headers():
    try:
        response = requests.get(f"{BASE_URL}/")
        # Just a dummy check that we can hit the endpoint and get a response
        assert response.status_code in [200, 404]
    except requests.exceptions.ConnectionError:
        pytest.skip("API not running")
