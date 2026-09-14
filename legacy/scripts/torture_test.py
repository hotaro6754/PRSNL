import requests
import json
import time

API_URL = "http://localhost:8000/api/scan"

payloads = [
    {"name": "Benign URL", "type": "url", "content": "https://en.wikipedia.org/wiki/Computer_security"},
    {"name": "Suspicious URL", "type": "url", "content": "http://verify-account-update.apple.com.badsite.tk/login"},
    {"name": "SSRF Cloud Metadata", "type": "url", "content": "http://169.254.169.254/latest/meta-data"},
    {"name": "Localhost SSRF", "type": "url", "content": "http://127.0.0.1:22"},
    {"name": "Benign SMS", "type": "sms", "content": "Hey, are we still on for dinner tonight?"},
    {"name": "Malicious SMS", "type": "sms", "content": "URGENT: Your account suspended. Click here to verify now: http://secure-update-login-apple.com.badsite.tk"},
    {"name": "Malformed Type", "type": "unknown", "content": "test"},
]

print("Waiting for API to become available...")
for _ in range(30):
    try:
        if requests.get("http://localhost:8000/health").status_code == 200:
            break
    except:
        time.sleep(2)

print("\n--- STARTING TORTURE TEST ---")
for p in payloads:
    print(f"Testing: {p['name']}")
    try:
        resp = requests.post(API_URL, json={"type": p.get("type", "url"), "content": p["content"]})
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Risk Score: {data.get('risk_score')}")
            print(f"  Status: {data.get('status')}")
            # check for DEGRADED or UNAVAILABLE in evidence
            for ev in data.get('evidence', []):
                if isinstance(ev.get('explanation'), str) and ('DEGRADED' in ev['explanation'] or 'UNAVAILABLE' in ev['explanation']):
                    print(f"  [DEGRADED/UNAVAILABLE DETECTED] Feature: {ev['feature']}")
        else:
            print(f"  Error Response: {resp.text[:100]}")
    except Exception as e:
        print(f"  CRASH/EXCEPTION: {str(e)}")
