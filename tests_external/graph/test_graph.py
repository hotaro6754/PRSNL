import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_graph_construction():
    try:
        response = requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        pytest.skip("API not running")
        
    assert response.status_code == 200, "Health check failed"
