import requests
import sys

def run_tests():
    all_passed = True

    print("--- Running E2E Tests ---")

    # 1. Frontend Routes
    # http://localhost:3000/ (Dashboard)
    try:
        r = requests.get("http://localhost:3000/")
        assert r.status_code == 200, f"Status Code: {r.status_code}"
        text = r.text
        assert "GRAFANA" in text, "GRAFANA missing"
        assert "PROMETHEUS" in text, "PROMETHEUS missing"
        assert "IP ADDRESSING" in text, "IP ADDRESSING missing"
        print("[PASS] Frontend: Dashboard (/)")
    except Exception as e:
        print(f"[FAIL] Frontend: Dashboard (/) - {e}")
        all_passed = False

    # http://localhost:3000/simulator
    try:
        r = requests.get("http://localhost:3000/simulator")
        assert r.status_code == 200, f"Status Code: {r.status_code}"
        text = r.text
        assert "Action Center" in text, "Action Center missing"
        assert "Aggressive Port Scan" in text, "Aggressive Port Scan missing"
        print("[PASS] Frontend: Simulator (/simulator)")
    except Exception as e:
        print(f"[FAIL] Frontend: Simulator (/simulator) - {e}")
        all_passed = False

    # http://localhost:3000/scan
    try:
        r = requests.get("http://localhost:3000/scan")
        assert r.status_code == 200, f"Status Code: {r.status_code}"
        text = r.text
        assert "Risk Intelligence Engine" in text, "Risk Intelligence Engine missing"
        assert "EXPLAINABLE FRAUD" in text, "EXPLAINABLE FRAUD missing"
        print("[PASS] Frontend: Scan (/scan)")
    except Exception as e:
        print(f"[FAIL] Frontend: Scan (/scan) - {e}")
        all_passed = False

    # 2. Backend APIs
    # GET http://localhost:8000/api/network/tunnels
    try:
        r = requests.get("http://localhost:8000/api/network/tunnels")
        assert r.status_code == 200, f"Status Code: {r.status_code}"
        data = r.json()
        assert "monitored_ips" in data, "monitored_ips missing"
        assert "one_way_tunnels" in data, "one_way_tunnels missing"
        print("[PASS] Backend: /api/network/tunnels")
    except Exception as e:
        print(f"[FAIL] Backend: /api/network/tunnels - {e}")
        all_passed = False

    # POST http://localhost:8000/api/scan
    try:
        r = requests.post("http://localhost:8000/api/scan", json={"type": "url", "content": "http://evil.com"})
        assert r.status_code == 200, f"Status Code: {r.status_code}"
        data = r.json()
        assert "explanation" in data, "explanation missing"
        assert "education" in data, "education missing"
        assert "recommendations" in data, "recommendations missing"
        assert "evidence" in data, "evidence missing"
        print("[PASS] Backend: /api/scan")
    except Exception as e:
        print(f"[FAIL] Backend: /api/scan - {e}")
        all_passed = False

    # POST http://localhost:8000/api/simulate/qr
    try:
        r = requests.post("http://localhost:8000/api/simulate/qr")
        assert r.status_code == 200, f"Status Code: {r.status_code}"
        print("[PASS] Backend: /api/simulate/qr")
    except Exception as e:
        print(f"[FAIL] Backend: /api/simulate/qr - {e}")
        all_passed = False

    if all_passed:
        print("\nAll tests PASSED.")
        sys.exit(0)
    else:
        print("\nSome tests FAILED.")
        sys.exit(1)

if __name__ == '__main__':
    run_tests()
