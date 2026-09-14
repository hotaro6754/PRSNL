import httpx
import time
import json
import uuid

tests = []
def add_test(cat, type_str, content):
    tests.append({"category": cat, "type": type_str, "content": content})

# URL
add_test("URL", "url", "https://www.example.org/")
add_test("URL", "url", "https://legit-site.com/deep/path/index.html?user=123")
add_test("URL", "url", "https://legit-site.com/" + "a"*200)
add_test("URL", "url", "https://zxcvbnm12345.legit.com/")
add_test("URL", "url", "http://127.0.0.1/") # SSRF
add_test("URL", "url", "http://xn--80ak6aa92e.com/") # punycode
add_test("URL", "url", "https://google.com\u2044search") # confusable
add_test("URL", "url", "https://login.verify.account.security.legit.com/")
add_test("URL", "url", "https://legit.com/login/verify/account")
add_test("URL", "url", "https://legit.com/%61%64%6d%69%6e")
add_test("URL", "url", "https://bit.ly/3xyz")
add_test("URL", "url", "https://tinyurl.com/a")
add_test("URL", "url", "not-a-url")
add_test("URL", "url", "file:///etc/passwd")
add_test("URL", "url", "http://169.254.169.254/latest/meta-data")

# EMAIL
add_test("EMAIL", "email", "Hello, just checking in.")
add_test("EMAIL", "email", "<html><body>Click <a href='http://legit.com'>here</a></body></html>")
add_test("EMAIL", "email", "From: admin@evil.com\nReply-To: bad@evil.com\nHello.")
add_test("EMAIL", "email", "From: \"PayPal Support\" <admin@evil.com>\nHello.")
add_test("EMAIL", "email", "Received-SPF: fail (domain of evil.com does not designate X as permitted sender)")
add_test("EMAIL", "email", "DKIM-Signature: v=1; a=rsa-sha256; d=evil.com; s=bad;")
add_test("EMAIL", "email", "DMARC: fail")
add_test("EMAIL", "email", "Please verify your credentials at http://evil.com/login")
add_test("EMAIL", "email", "See attached invoice.exe")
add_test("EMAIL", "email", "Links: http://a.com http://b.com http://c.com")
add_test("EMAIL", "email", "Content-Type: multipart/mixed; boundary=\"broken")
add_test("EMAIL", "email", "")

# SMS
add_test("SMS", "sms", "Your verification code is 123456.")
add_test("SMS", "sms", "Your package is arriving today.")
add_test("SMS", "sms", "Bank alert: A withdrawal of  was made.")
add_test("SMS", "sms", "URGENT: Your account suspended. Click here http://evil.com")
add_test("SMS", "sms", "KYC suspended. Update PAN at http://pan-update.com")
add_test("SMS", "sms", "Reply with your password to verify.")
add_test("SMS", "sms", "Send  to this BTC address.")
add_test("SMS", "sms", "Click bit.ly/xxx for free money.")
add_test("SMS", "sms", "Your áccount is l0cked.")
add_test("SMS", "sms", "Hello नमस्ते click here")
add_test("SMS", "sms", "A" * 500)
add_test("SMS", "sms", "")

# QR
add_test("QR", "qr", "https://example.org/")
add_test("QR", "qr", "Just some plain text in a QR.")
add_test("QR", "qr", "WIFI:S:MyNetwork;T:WPA;P:password;;")
add_test("QR", "qr", "upi://pay?pa=scammer@upi&pn=Scammer")
add_test("QR", "qr", "https://evil-qr.phishing.com/login")
add_test("QR", "qr", "ROTATED_QR_PAYLOAD")
add_test("QR", "qr", "LOW_RES_QR")
add_test("QR", "qr", "DAMAGED_QR")
add_test("QR", "qr", "OBSCURED_QR")
add_test("QR", "qr", "MALFORMED_IMAGE_DATA")

# WEB
add_test("WEB", "url", "https://example.org/")
add_test("WEB", "url", "https://github.com/login")
add_test("WEB", "url", "http://credential-harvesting.lab.local")
add_test("WEB", "url", "http://js-form.lab.local")
add_test("WEB", "url", "http://iframe-heavy.lab.local")
add_test("WEB", "url", "http://redirect.lab.local")
add_test("WEB", "url", "http://external-scripts.lab.local")
add_test("WEB", "url", "http://slow-page.lab.local")
add_test("WEB", "url", "http://ssrf-redirect.lab.local")
add_test("WEB", "url", "http://resource-exhaustion.lab.local")

# SOCIAL
add_test("SOCIAL", "sms", "Company picnic this Friday!")
add_test("SOCIAL", "sms", "I am Elon Musk, send ETH.")
add_test("SOCIAL", "sms", "You won an iPhone! Click here.")
add_test("SOCIAL", "sms", "Guaranteed 500% ROI in crypto.")
add_test("SOCIAL", "sms", "Login here: http://fake-login.com")
add_test("SOCIAL", "sms", "h**p://obfuscated[.]link/scam")

results = []
client = httpx.Client(timeout=10.0)

for idx, t in enumerate(tests):
    t_id = f"{t['category']}-{str(idx+1).zfill(3)}"
    try:
        start = time.time()
        resp = client.post("http://127.0.0.1:8000/api/scan", json={"type": t['type'], "content": t['content']})
        end = time.time()
        results.append({
            "test_id": t_id,
            "category": t['category'],
            "status": "PASS" if resp.status_code == 200 else "DEGRADED",
            "latency": end - start,
            "response": resp.json() if resp.status_code == 200 else None
        })
    except Exception as e:
        results.append({
            "test_id": t_id,
            "category": t['category'],
            "status": "FAIL",
            "error": str(e)
        })

with open("scripts/torture/results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Executed {len(tests)} API scans.")
