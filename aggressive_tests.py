import asyncio
import httpx
import time
import jwt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_BASE = "http://127.0.0.1:8000"

def get_token():
    payload = {
        "sub": "admin",
        "org_id": "tenant-1",
        "scopes": ["admin"]
    }
    return jwt.encode(payload, "supersecretkey", algorithm="HS256")

TESTS = [
    {"type": "simulate", "attack": "qr", "desc": "1. Aggressive QR Quishing generation"},
    {"type": "simulate", "attack": "sms", "desc": "2. Aggressive SMS Smishing blast"},
    {"type": "simulate", "attack": "email", "desc": "3. Aggressive Email Phishing payload"},
    {"type": "simulate", "attack": "uni_directional", "desc": "4. Uni-directional IP scanning (SYN flood)"},
    {"type": "simulate", "attack": "port_scan", "desc": "5. Standard Port Scan"},
    {"type": "simulate", "attack": "dga", "desc": "6. DGA Beaconing Simulation"},
    {"type": "scan", "scan_type": "url", "content": "http://evil-dga-domain.net/login.php", "desc": "7. Direct malicious URL ingestion"},
    {"type": "scan", "scan_type": "qr", "content": "https://paypal-update-urgent.com/qr", "desc": "8. Direct malicious QR string"},
    {"type": "scan", "scan_type": "email", "content": "From: admin@evil.com\nSubject: Wire Transfer\n\nPlease transfer  immediately.", "desc": "9. Direct malicious Email string"},
    {"type": "scan", "scan_type": "sms", "content": "Alert: Netflix account suspended. Renew at http://n3tflix-renew.co", "desc": "10. Direct malicious SMS string"},
    {"type": "simulate", "attack": "brute_force", "desc": "11. SSH Brute Force"},
    {"type": "scan", "scan_type": "url", "content": "http://192.168.1.1/admin", "desc": "12. SSRF Attack URL"},
    {"type": "scan", "scan_type": "url", "content": "http://malware-distribution.com/payload.exe", "desc": "13. Malware delivery URL"},
    {"type": "scan", "scan_type": "qr", "content": "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?amount=50", "desc": "14. Cryptocurrency Extortion QR"},
    {"type": "scan", "scan_type": "sms", "content": "FedEx: Your package is delayed. Pay .99 fee: https://fedx-tracker-fee.com", "desc": "15. Logistics SMS Phishing"},
    {"type": "scan", "scan_type": "email", "content": "Urgent Invoice Attached. Click here to download.", "desc": "16. Generic Invoice Email Phishing"},
    {"type": "simulate", "attack": "uni_directional", "desc": "17. Uni-directional IP scanning (Round 2)"},
    {"type": "simulate", "attack": "qr", "desc": "18. Aggressive QR Quishing generation (Round 2)"},
    {"type": "simulate", "attack": "sms", "desc": "19. Aggressive SMS Smishing blast (Round 2)"},
    {"type": "scan", "scan_type": "email", "content": "You have a secure message from HR. Login to view: http://hr-portal-sso.com", "desc": "20. HR Portal Phishing"},
    {"type": "simulate", "attack": "dga", "desc": "21. DGA Beaconing Simulation (Round 2)"},
    {"type": "scan", "scan_type": "url", "content": "http://localhost:8000/api/admin", "desc": "22. Localhost SSRF probe"},
    {"type": "simulate", "attack": "port_scan", "desc": "23. Intense Port Scan (Round 2)"},
    {"type": "scan", "scan_type": "qr", "content": "WIFI:S:Free_Airport_WiFi;T:WPA;P:hacked123;;", "desc": "24. Malicious WiFi QR profile"},
    {"type": "scan", "scan_type": "sms", "content": "Bank Alert: Unrecognized login attempt. Verify identity: http://chase-security-verify.com", "desc": "25. Bank Smishing"},
    {"type": "scan", "scan_type": "email", "content": "Subject: Password Expiry Notification\nYour password expires in 24 hours. Reset it here: http://sso-update-passwd.com", "desc": "26. Credential Harvesting Email"},
    {"type": "simulate", "attack": "uni_directional", "desc": "27. Uni-directional IP scanning (Round 3)"},
    {"type": "simulate", "attack": "brute_force", "desc": "28. SSH Brute Force (Round 2)"},
    {"type": "scan", "scan_type": "url", "content": "https://pastebin.com/raw/malicious_payload", "desc": "29. Pastebin Payload Delivery"},
    {"type": "simulate", "attack": "qr", "desc": "30. Aggressive QR Quishing generation (Round 3)"}
]

async def run_tests():
    logging.info("Starting 30 Aggressive Module Tests...")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    success_count = 0
    async with httpx.AsyncClient(timeout=10.0) as client:
        for i, test in enumerate(TESTS):
            logging.info(f"Executing Test {i+1}: {test['desc']}")
            try:
                if test["type"] == "simulate":
                    res = await client.post(f"{API_BASE}/api/simulate/{test['attack']}", headers=headers)
                    if res.status_code in (200, 202):
                        success_count += 1
                        logging.info(f"  -> SUCCESS (Simulate {test['attack']} triggered)")
                    else:
                        logging.error(f"  -> FAILED: HTTP {res.status_code} - {res.text}")
                elif test["type"] == "scan":
                    res = await client.post(f"{API_BASE}/api/scan", json={"type": test["scan_type"], "content": test["content"]}, headers=headers)
                    if res.status_code in (200, 201):
                        success_count += 1
                        logging.info(f"  -> SUCCESS (Scan {test['scan_type']} completed)")
                    else:
                        logging.error(f"  -> FAILED: HTTP {res.status_code} - {res.text}")
            except Exception as e:
                logging.error(f"  -> EXCEPTION: {str(e)}")
            await asyncio.sleep(0.2)
            
    logging.info(f"Completed! {success_count}/{len(TESTS)} tests succeeded.")

if __name__ == '__main__':
    asyncio.run(run_tests())
