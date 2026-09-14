import requests
import time
import json
import base64

API_URL = "http://localhost:8000/api/scan"

def test_url(name, url, expected_status=200):
    print(f"\\nTesting: {name}")
    print(f"URL: {url}")
    try:
        resp = requests.post(API_URL, json={"type": "url", "content": url}, timeout=20)
        if resp.status_code != expected_status:
            print(f"  [FAIL] Expected {expected_status}, got {resp.status_code}")
            return
            
        data = resp.json()
        print(f"  Risk Score: {data.get('risk_score')}")
        
        # Look for Playwright evidence
        pw_evidence = [e for e in data.get('evidence', []) if e.get('evidence_type', '').startswith('Playwright')]
        if pw_evidence:
            for ev in pw_evidence:
                status = ev.get('details', {}).get('status', 'SUCCESS (Implied)')
                reason = ev.get('details', {}).get('reason', '')
                print(f"  [PLAYWRIGHT] Type: {ev['evidence_type']} | Status: {status} | Reason: {reason}")
        else:
            print("  [PLAYWRIGHT] No Playwright evidence found!")
            
    except Exception as e:
        print(f"  Request failed: {e}")

print("Waiting for API to become available...")
time.sleep(2)

print("\\n--- STARTING V2 TORTURE TEST ---")

# 1. Benign Static Page (Data URI)
html_static = "<html><body><h1>Benign Static</h1><p>Safe content</p></body></html>"
url_static = f"data:text/html;base64,{base64.b64encode(html_static.encode()).decode()}"
test_url("Benign Static Page (LAB)", url_static)

# 2. Controlled Fake Login (Data URI)
html_login = "<html><body><form><input type='text'/><input type='password'/></form></body></html>"
url_login = f"data:text/html;base64,{base64.b64encode(html_login.encode()).decode()}"
test_url("Controlled Fake Login (LAB)", url_login)

# 3. Public Benign Page
test_url("Public Benign Page", "http://example.com")

# 4. SSRF Localhost
test_url("SSRF Localhost", "http://127.0.0.1")

# 5. SSRF Cloud Metadata
test_url("SSRF Cloud Metadata", "http://169.254.169.254/latest/meta-data")

