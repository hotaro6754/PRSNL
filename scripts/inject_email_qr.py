import httpx
import time

print("Injecting Email scan...")
httpx.post("http://127.0.0.1:8000/api/scan", json={"type": "email", "content": "Dear user, wire transfer required immediately. See attached invoice.exe"})
time.sleep(1)

print("Injecting QR scan...")
httpx.post("http://127.0.0.1:8000/api/scan", json={"type": "qr", "content": "https://evil-qr.phishing.com/login"})
time.sleep(1)

print("Done.")
