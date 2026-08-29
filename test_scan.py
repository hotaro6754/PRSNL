import requests
import json

payload = {
    "type": "email",
    "content": "URGENT: Your account is suspended. Click here http://paypal-verify.account-security.xyz/login immediately to update your password and transfer your balance."
}

try:
    response = requests.post("http://localhost:8000/api/scan", json=payload)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
