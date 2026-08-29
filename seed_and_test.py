"""
CyberOS — Seed Historical Detection Logs + Run 15 Aggressive Module Tests
Seeds yesterday's and today's logs into MongoDB, then fires 15 live scan tests.
"""
import asyncio
import httpx
import jwt
import logging
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
import random
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_BASE = "http://127.0.0.1:8000"
MONGO_URI = "mongodb://127.0.0.1:27017/"
SECRET = "supersecretkey"

# ─── HISTORICAL LOG DATA ────────────────────────────────────────────────
def seed_historical_logs():
    """Seed yesterday's + today's detection logs into MongoDB."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = client["cyberos"]
    col = db["detection_logs"]

    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    ATTACKER_IPS_TODAY = [
        "185.220.101.34", "45.154.255.147", "91.240.118.172",
        "194.26.135.89", "23.129.64.210", "162.247.74.27",
        "198.98.56.149", "109.70.100.33", "176.10.104.240",
        "51.75.64.23",
    ]
    ATTACKER_IPS_YESTERDAY = [
        "103.253.41.98", "185.100.87.202", "37.120.198.219",
        "178.20.55.16", "46.166.139.111", "80.67.172.162",
        "209.141.45.189", "5.2.69.50", "193.218.118.190",
        "77.247.181.163",
    ]
    ATTACKER_IPS_TOMORROW = [
        "212.21.66.6", "95.211.230.211", "185.129.61.1",
        "45.33.32.156", "104.244.76.13", "199.249.230.87",
        "171.25.193.77", "62.210.105.116", "185.220.102.8",
        "192.42.116.16",
    ]

    THREAT_TYPES = [
        {"type": "url", "module": "URL Scanner", "severity": "critical", "category": "phishing"},
        {"type": "email", "module": "Email Analyzer", "severity": "high", "category": "phishing_email"},
        {"type": "sms", "module": "SMS Analyzer", "severity": "high", "category": "smishing"},
        {"type": "qr", "module": "QR Scanner", "severity": "critical", "category": "quishing"},
        {"type": "url", "module": "URL Scanner", "severity": "medium", "category": "malware_delivery"},
        {"type": "network", "module": "NDR Engine", "severity": "critical", "category": "port_scan"},
        {"type": "network", "module": "NDR Engine", "severity": "high", "category": "brute_force"},
        {"type": "network", "module": "NDR Engine", "severity": "critical", "category": "dga_beaconing"},
        {"type": "network", "module": "NDR Engine", "severity": "high", "category": "uni_directional"},
        {"type": "url", "module": "URL Scanner", "severity": "critical", "category": "ssrf_attempt"},
        {"type": "email", "module": "Email Analyzer", "severity": "critical", "category": "credential_harvest"},
        {"type": "sms", "module": "SMS Analyzer", "severity": "medium", "category": "bank_fraud"},
        {"type": "qr", "module": "QR Scanner", "severity": "high", "category": "crypto_extortion"},
        {"type": "url", "module": "Web Analyzer", "severity": "critical", "category": "drive_by_download"},
        {"type": "network", "module": "NDR Engine", "severity": "critical", "category": "c2_beaconing"},
    ]

    PAYLOADS = {
        "phishing": "http://secure-paypal-update.com/login.php",
        "phishing_email": "From: admin@company.com\nSubject: Urgent Wire Transfer\nPlease wire $50,000 to account 4839201.",
        "smishing": "URGENT: Your bank account is locked. Verify at http://chase-verify-now.com",
        "quishing": "https://bit.ly/3xF4k3d-bank-verify",
        "malware_delivery": "http://cdn.malware-distribution.net/payload.exe",
        "port_scan": "TCP SYN scan detected on ports 22,80,443,3389,8080,8443",
        "brute_force": "22 failed SSH login attempts from source in 60s window",
        "dga_beaconing": "DNS queries to xk3j9f.evil.com, p8m2d1.evil.com, r7n5q4.evil.com",
        "uni_directional": "Unidirectional TCP flow: 847 SYN packets, 0 SYN-ACK responses",
        "ssrf_attempt": "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
        "credential_harvest": "Subject: Password Expiry\nClick to reset: http://sso-corporate-reset.com/auth",
        "bank_fraud": "Alert: ₹49,999 debited from A/C XX4521. Not you? Call 1800-FRAUD-NOW",
        "crypto_extortion": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.5",
        "drive_by_download": "http://compromised-wordpress.com/wp-content/uploads/trojan.js",
        "c2_beaconing": "Periodic HTTPS POST to 185.220.101.34:443 every 60s (C2 pattern)",
    }

    VERDICTS = ["malicious", "suspicious", "malicious", "malicious", "suspicious"]

    logs = []

    # Generate yesterday's logs (25 entries)
    for i in range(25):
        threat = random.choice(THREAT_TYPES)
        ip = random.choice(ATTACKER_IPS_YESTERDAY)
        ts = yesterday + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
        logs.append({
            "_id": str(uuid.uuid4()),
            "timestamp": ts.isoformat() + "Z",
            "source_ip": ip,
            "destination_ip": f"10.0.{random.randint(1,5)}.{random.randint(10,250)}",
            "type": threat["type"],
            "module": threat["module"],
            "severity": threat["severity"],
            "category": threat["category"],
            "payload": PAYLOADS.get(threat["category"], "N/A"),
            "verdict": random.choice(VERDICTS),
            "risk_score": round(random.uniform(0.65, 0.99), 2),
            "ml_confidence": round(random.uniform(0.70, 0.98), 2),
            "model": "XGBoost-v3.2" if random.random() > 0.3 else "IsolationForest-v2.1",
            "evidence_id": f"EV-{uuid.uuid4().hex[:8].upper()}",
            "case_id": f"CASE-{random.randint(1000, 9999)}",
            "status": random.choice(["open", "investigating", "resolved"]),
            "day": "yesterday",
        })

    # Generate today's logs (30 entries)
    for i in range(30):
        threat = random.choice(THREAT_TYPES)
        ip = random.choice(ATTACKER_IPS_TODAY)
        ts = now.replace(hour=0) + timedelta(hours=random.randint(0, now.hour), minutes=random.randint(0, 59))
        logs.append({
            "_id": str(uuid.uuid4()),
            "timestamp": ts.isoformat() + "Z",
            "source_ip": ip,
            "destination_ip": f"10.0.{random.randint(1,5)}.{random.randint(10,250)}",
            "type": threat["type"],
            "module": threat["module"],
            "severity": threat["severity"],
            "category": threat["category"],
            "payload": PAYLOADS.get(threat["category"], "N/A"),
            "verdict": random.choice(VERDICTS),
            "risk_score": round(random.uniform(0.65, 0.99), 2),
            "ml_confidence": round(random.uniform(0.70, 0.98), 2),
            "model": "XGBoost-v3.2" if random.random() > 0.3 else "IsolationForest-v2.1",
            "evidence_id": f"EV-{uuid.uuid4().hex[:8].upper()}",
            "case_id": f"CASE-{random.randint(1000, 9999)}",
            "status": random.choice(["open", "investigating"]),
            "day": "today",
        })

    # Generate tomorrow's scheduled threat intel (10 entries)
    for i in range(10):
        threat = random.choice(THREAT_TYPES)
        ip = random.choice(ATTACKER_IPS_TOMORROW)
        ts = tomorrow.replace(hour=0) + timedelta(hours=random.randint(0, 12), minutes=random.randint(0, 59))
        logs.append({
            "_id": str(uuid.uuid4()),
            "timestamp": ts.isoformat() + "Z",
            "source_ip": ip,
            "destination_ip": f"10.0.{random.randint(1,5)}.{random.randint(10,250)}",
            "type": threat["type"],
            "module": threat["module"],
            "severity": threat["severity"],
            "category": threat["category"],
            "payload": PAYLOADS.get(threat["category"], "N/A"),
            "verdict": "predicted",
            "risk_score": round(random.uniform(0.50, 0.85), 2),
            "ml_confidence": round(random.uniform(0.55, 0.80), 2),
            "model": "ThreatIntel-Predictive-v1.0",
            "evidence_id": f"EV-{uuid.uuid4().hex[:8].upper()}",
            "case_id": f"CASE-{random.randint(1000, 9999)}",
            "status": "predicted",
            "day": "tomorrow",
        })

    col.drop()
    col.insert_many(logs)
    logging.info(f"Seeded {len(logs)} historical detection logs into MongoDB (yesterday={25}, today={30}, tomorrow={10})")

    # Also seed into the alerts collection for the frontend
    alerts_col = db["alerts"]
    alerts_col.drop()
    alerts_col.insert_many(logs)
    logging.info(f"Seeded {len(logs)} alerts into alerts collection")

    # Seed cases collection
    cases_col = db["cases"]
    cases = []
    case_ids = list(set(l["case_id"] for l in logs))
    for cid in case_ids[:15]:
        related = [l for l in logs if l["case_id"] == cid]
        cases.append({
            "_id": cid,
            "case_id": cid,
            "title": f"Investigation: {related[0]['category'].replace('_', ' ').title()}",
            "severity": related[0]["severity"],
            "status": related[0]["status"],
            "created_at": related[0]["timestamp"],
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "evidence_count": len(related),
            "source_ips": list(set(r["source_ip"] for r in related)),
            "modules_triggered": list(set(r["module"] for r in related)),
            "risk_score": max(r["risk_score"] for r in related),
        })
    cases_col.drop()
    cases_col.insert_many(cases)
    logging.info(f"Seeded {len(cases)} investigation cases")

# ─── 15 LIVE MODULE TESTS ───────────────────────────────────────────────
TESTS = [
    # URL Scans
    {"type": "scan", "scan_type": "url", "content": "http://evil-phishing-bank.com/login.php", "desc": "1. Phishing URL — Fake banking portal"},
    {"type": "scan", "scan_type": "url", "content": "http://malware-cdn.darknet.ru/payload.exe", "desc": "2. Malware URL — Drive-by download"},
    {"type": "scan", "scan_type": "url", "content": "http://169.254.169.254/latest/meta-data/", "desc": "3. SSRF Probe — AWS metadata theft"},
    # QR Scans
    {"type": "scan", "scan_type": "qr", "content": "https://paypal-verify-urgent.com/qr-auth", "desc": "4. QR Quishing — PayPal credential theft"},
    {"type": "scan", "scan_type": "qr", "content": "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?amount=2.5", "desc": "5. QR Crypto Extortion — Bitcoin ransom"},
    {"type": "scan", "scan_type": "qr", "content": "WIFI:S:Corporate_Guest;T:WPA;P:hacked_password;;", "desc": "6. QR WiFi Injection — Rogue AP config"},
    # Email Scans
    {"type": "scan", "scan_type": "email", "content": "From: ceo@company.com\nSubject: Urgent Wire Transfer\n\nPlease wire $125,000 to the following account immediately. Do not discuss with anyone.", "desc": "7. Email BEC — CEO fraud wire transfer"},
    {"type": "scan", "scan_type": "email", "content": "Subject: Password Expiry Notification\n\nYour corporate password expires in 2 hours.\nReset it here: http://sso-corp-reset.phishing.com/auth", "desc": "8. Email Credential Harvest — SSO phishing"},
    {"type": "scan", "scan_type": "email", "content": "Subject: Invoice #INV-29381\n\nPlease find attached invoice. Open the macro-enabled document to proceed.", "desc": "9. Email Malware — Invoice macro attack"},
    # SMS Scans
    {"type": "scan", "scan_type": "sms", "content": "ALERT: ₹49,999 debited from A/C XX4521. Not you? Click http://bank-refund-verify.com to claim refund.", "desc": "10. SMS Bank Fraud — Fake debit alert"},
    {"type": "scan", "scan_type": "sms", "content": "FedEx: Your package couldn't be delivered. Pay $1.99 fee: https://fedx-redelivery-fee.com", "desc": "11. SMS Logistics Phishing — Delivery scam"},
    {"type": "scan", "scan_type": "sms", "content": "Netflix: Your subscription payment failed. Update billing: http://n3tfl1x-billing.com/update", "desc": "12. SMS Subscription Scam — Netflix fraud"},
    # Simulations (network-level)
    {"type": "simulate", "attack": "port_scan", "desc": "13. Network — Aggressive port scan simulation"},
    {"type": "simulate", "attack": "dga", "desc": "14. Network — DGA beaconing C2 simulation"},
    {"type": "simulate", "attack": "brute_force", "desc": "15. Network — SSH brute force simulation"},
]


async def run_15_tests():
    logging.info("=" * 60)
    logging.info("STARTING 15 AGGRESSIVE MODULE TESTS")
    logging.info("=" * 60)

    token = jwt.encode({"sub": "admin", "org_id": "tenant-1", "scopes": ["admin"]}, SECRET, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}

    results = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        for i, test in enumerate(TESTS):
            logging.info(f"[{i+1}/15] {test['desc']}")
            try:
                if test["type"] == "simulate":
                    res = await client.post(f"{API_BASE}/api/simulate/{test['attack']}", headers=headers)
                else:
                    res = await client.post(f"{API_BASE}/api/scan", json={"type": test["scan_type"], "content": test["content"]}, headers=headers)

                if res.status_code in (200, 201, 202):
                    data = res.json()
                    verdict = data.get("verdict", data.get("status", "triggered"))
                    risk = data.get("risk_score", data.get("risk", "N/A"))
                    logging.info(f"  ✅ PASS — HTTP {res.status_code} | Verdict: {verdict} | Risk: {risk}")
                    results.append({"test": test["desc"], "status": "PASS", "http": res.status_code, "verdict": verdict, "risk": risk})
                else:
                    logging.error(f"  ❌ FAIL — HTTP {res.status_code} | {res.text[:100]}")
                    results.append({"test": test["desc"], "status": "FAIL", "http": res.status_code})
            except Exception as e:
                logging.error(f"  ❌ EXCEPTION — {str(e)[:100]}")
                results.append({"test": test["desc"], "status": "ERROR", "error": str(e)[:100]})
            await asyncio.sleep(0.3)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] != "PASS")
    logging.info("=" * 60)
    logging.info(f"RESULTS: {passed}/15 PASSED | {failed}/15 FAILED")
    logging.info("=" * 60)

    for r in results:
        status_icon = "✅" if r["status"] == "PASS" else "❌"
        logging.info(f"  {status_icon} {r['test']}")

    return results


if __name__ == "__main__":
    logging.info("Phase 1: Seeding historical detection logs...")
    seed_historical_logs()
    logging.info("")
    logging.info("Phase 2: Running 15 live module tests...")
    asyncio.run(run_15_tests())
