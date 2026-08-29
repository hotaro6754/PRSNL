import requests
import time
import json
import os

print("Waiting for backend API...")
while True:
    try:
        r = requests.get('http://localhost:8000/health')
        if r.status_code == 200:
            break
    except:
        time.sleep(1)

cases = [
    {"name": "1. Standard Safe URL", "type": "url", "content": "https://www.google.com/"},
    {"name": "2. Obvious Phishing DGA", "type": "url", "content": "http://secure-login-update-paypal.com.xsdf9823hfjshd.xyz/auth/verify?token=19283"},
    {"name": "3. SSRF AWS Metadata", "type": "url", "content": "http://169.254.169.254/latest/meta-data/"},
    {"name": "4. Typosquatting Brand", "type": "url", "content": "https://www.micros0ft.com/login"},
    {"name": "5. Standard Safe SMS", "type": "url", "content": "Hey mom, I will be home by 5 PM. Can you make dinner?"},
    {"name": "6. Urgent Smishing Bank", "type": "sms", "content": "URGENT: Your HDFC bank account will be suspended in 24 hours due to suspicious activity. Please verify your KYC details immediately at http://hdfc-kyc-update-now.net"},
    {"name": "7. Fake Package Delivery", "type": "sms", "content": "FedEx: Your package delivery failed. Click here to reschedule and pay the .99 fee: http://fedex-redelivery.info"},
    {"name": "8. Standard Safe Email", "type": "email", "content": "Hi team, please find attached the meeting notes from yesterday."},
    {"name": "9. CEO Fraud / BEC", "type": "email", "content": "From: CEO <ceo.company.external@gmail.com>\nTo: Finance\nSubject: STRICTLY CONFIDENTIAL\n\nI need you to urgently wire ,000 to our new vendor in Singapore. Send the confirmation receipt by 2PM."},
    {"name": "10. Fake Invoice Email", "type": "email", "content": "Please review the attached invoice for ,299. Action required immediately or your account will be suspended."},
    {"name": "11. Standard Safe QR (Text)", "type": "qr", "content": "Welcome to the conference! WiFi password is: welcome2026"},
    {"name": "12. Rogue WiFi QR", "type": "qr", "content": "WIFI:T:WPA;S:Free Airport WiFi;P:;H:true;"},
    {"name": "13. Quishing URL QR", "type": "qr", "content": "https://secure-login-update-paypal.com.xsdf9823hfjshd.xyz/qr-auth"},
]

simulations = [
    {"name": "14. Zeek Port Scan (Internal Sensor)", "type": "sim", "content": "port_scan"},
    {"name": "15. Zeek SSH Brute Force (Internal Sensor)", "type": "sim", "content": "brute_force"}
]

if os.path.exists('fresh_logs.txt'):
    os.remove('fresh_logs.txt')

results = []
with open('fresh_logs.txt', 'w') as f:
    f.write("=== CYBEROS HACKSPRINT EXHAUSTIVE 15-CASE TEST LOG ===\n\n")
    
    for c in cases:
        print(f"Testing {c['name']}...")
        r = requests.post('http://localhost:8000/api/scan', json={"type": c['type'], "content": c['content']})
        if r.status_code == 200:
            data = r.json()
            score = data.get('risk_score', 0)
            summary = data.get('title', '')
            f.write(f"CASE: {c['name']}\nTYPE: {c['type'].upper()}\nSCORE: {score:.2f} / 1.0\nSUMMARY: {summary}\n")
            f.write(f"EVIDENCE: {[e.get('evidence_type', e.get('feature')) for e in data.get('evidence_ledger', [])]}\n")
            f.write("-" * 50 + "\n")
        else:
            f.write(f"CASE: {c['name']} FAILED: {r.text}\n\n")
            
    for s in simulations:
        print(f"Testing {s['name']}...")
        r = requests.post(f'http://localhost:8000/api/simulate/{s["content"]}')
        if r.status_code == 200:
            f.write(f"CASE: {s['name']}\nTYPE: ZEEK SENSOR\nSTATUS: SIMULATION LAUNCHED (Check Dashboard for Network Correlator Logs)\n")
            f.write("-" * 50 + "\n")

print("Generated fresh_logs.txt")
