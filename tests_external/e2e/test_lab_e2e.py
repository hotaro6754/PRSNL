import requests
import time
import pytest

BASE_URL = "http://localhost:8000"

def test_gold_standard_e2e():
    # 1. Send real payload through the live API
    payload = {
        "type": "url",
        "content": "http://evil-phishing.com/login"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/scan", json=payload, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip("API not running, skipping e2e test")
        
    assert response.status_code in [200, 202], f"Unexpected status code: {response.status_code}"
    
    data = response.json()
    case_id = data.get("case_id")
    
    # Check that graph (attack_chain) was constructed and provenance/evidence was recorded
    assert data.get("attack_chain") is not None, "Graph (attack_chain) was not constructed"
    assert data.get("evidence") is not None, "Provenance/evidence was not recorded"
    assert case_id is not None, "Case ID missing"

