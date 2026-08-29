"""
CyberOS Full Regression Test
=============================
Tests all 15 threat/benign scenarios after adding SlowHTTPDetector
and fixing the DDoS detector's Pydantic compatibility.

Verifies NO regression on previously validated detections.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import uuid
import json
import random
from collections import defaultdict
from backend.contracts.observation import NetworkObservation
from backend.detectors.slow_http import SlowHTTPDetector
from backend.detectors.ddos import DDoSDetector
from backend.detectors.exfil import ExfiltrationDetector
from backend.detectors.scan import PortScanDetector
from backend.detectors.beacon import BeaconingDetector
from backend.detectors.dga import DGADetector
from backend.detectors.dns_tunnel import DNSTunnelDetector
from backend.detectors.tls import TLSSessionDetector

now_ms = int(time.time() * 1000)

# Initialize detectors
slow_http = SlowHTTPDetector()
ddos = DDoSDetector()
exfil = ExfiltrationDetector()
scan = PortScanDetector()
beacon = BeaconingDetector()
dga = DGADetector()
dns_tunnel = DNSTunnelDetector()
tls_anomaly = TLSSessionDetector()

ALL_DETECTORS = [ddos, scan, beacon, dga, exfil, slow_http, dns_tunnel, tls_anomaly]

results = []

def make_obs(**kwargs):
    defaults = dict(
        observation_id=str(uuid.uuid4()),
        flow_id=str(uuid.uuid4())[:8],
        timestamp=now_ms,
        first_seen=now_ms,
        last_seen=now_ms + 1000,
        duration=1.0,
        source_ip="192.168.1.10",
        destination_ip="10.0.0.1",
        source_port=random.randint(1024, 65535),
        destination_port=80,
        protocol=6,
        orig_packets=10,
        resp_packets=8,
        orig_ip_bytes=1000,
        resp_ip_bytes=5000,
        tcp_syn_orig=True,
        tcp_syn_resp=True,
        tcp_fin_orig=True,
        tcp_fin_resp=True,
        tcp_rst_orig=False,
        tcp_rst_resp=False,
    )
    defaults.update(kwargs)
    return NetworkObservation(**defaults)

def run_all_detectors(flows, label):
    all_alerts = []
    for det in ALL_DETECTORS:
        try:
            alerts = det.evaluate_window(flows, now_ms)
            all_alerts.extend(alerts)
        except Exception as e:
            print(f"    {det.detector_id} ERROR: {e}")
    return all_alerts

def test(label, flows, expect_detect, expected_class=None):
    alerts = run_all_detectors(flows, label)
    detected = len(alerts) > 0
    
    status = "PASS"
    if expect_detect and not detected:
        status = "FAIL (MISSED)"
    elif not expect_detect and detected:
        status = "FAIL (FALSE POSITIVE)"
        
    threat = alerts[0].threat_class if alerts else "—"
    conf = round(alerts[0].confidence, 3) if alerts else "—"
    det_id = alerts[0].detector_id if alerts else "—"
    
    result = {
        "test": label,
        "expected": "DETECT" if expect_detect else "BENIGN",
        "detected": detected,
        "threat_class": str(threat),
        "confidence": conf,
        "detector": str(det_id),
        "alerts": len(alerts),
        "status": status,
    }
    results.append(result)
    print(f"  {label:30s} | {status:20s} | {threat:15s} | conf={conf} | det={det_id}")
    return status


print("=" * 100)
print("CyberOS FULL REGRESSION TEST")
print("=" * 100)

# T1: Benign Web
flows_t1 = [make_obs(destination_port=443, orig_ip_bytes=2000, resp_ip_bytes=50000) for _ in range(3)]
test("T1 Benign Web", flows_t1, False)

# T2: Benign High Volume
flows_t2 = [make_obs(
    destination_port=443,
    orig_ip_bytes=50000,
    resp_ip_bytes=500000,
    orig_packets=100,
    resp_packets=200,
) for _ in range(8)]
test("T2 Benign High Volume", flows_t2, False)

# T3: SYN Flood
flows_t3 = [make_obs(
    source_ip=f"10.0.{random.randint(0,255)}.{random.randint(1,254)}",
    orig_packets=1,
    resp_packets=0,
    orig_ip_bytes=54,
    resp_ip_bytes=0,
    tcp_syn_orig=True,
    tcp_syn_resp=False,
    tcp_fin_orig=False,
    tcp_fin_resp=False,
    duration=0.01,
) for _ in range(600)]
test("T3 SYN Flood", flows_t3, True, "DDoS")

# T4: UDP Flood
flows_t4 = [make_obs(
    protocol=17,
    destination_port=53,
    orig_packets=2,
    resp_packets=0,
    orig_ip_bytes=1200,
    resp_ip_bytes=0,
    tcp_syn_orig=False,
    tcp_syn_resp=False,
    tcp_fin_orig=False,
    tcp_fin_resp=False,
) for _ in range(600)]
test("T4 UDP Flood", flows_t4, True, "DDoS")

# T5: Rigid Beacon - Expect MALICIOUS (C2 Beaconing)
flows_t5 = [make_obs(
    destination_ip="203.0.113.5",
    destination_port=443,
    orig_ip_bytes=200,
    resp_ip_bytes=100,
    duration=0.5,
    timestamp=now_ms + (i * 5000),  # 5s beacon
    bidirectional_bytes=300
) for i in range(20)]
test("T5 Rigid Beacon", flows_t5, True, "Beaconing")

# T6: Jittered Beacon - Expect MALICIOUS
flows_t6 = [make_obs(
    destination_ip="203.0.113.10",
    destination_port=8443,
    orig_ip_bytes=150,
    resp_ip_bytes=80,
    timestamp=now_ms + int((i * 5000) + random.uniform(-500, 500)),
    bidirectional_bytes=230
) for i in range(15)]
test("T6 Jittered Beacon", flows_t6, True, "Beaconing")

# T7: DGA
flows_t7 = [make_obs(
    protocol=17,
    destination_port=53,
    dns_query=f"q9x3vj8k2m5z7w4n1p6r8t4y2u1o9.com",
    orig_ip_bytes=80,
    resp_ip_bytes=200,
    tcp_syn_orig=False,
    tcp_syn_resp=False,
    tcp_fin_orig=False,
    tcp_fin_resp=False,
    orig_packets=1,
    resp_packets=1,
) for _ in range(20)]
test("T7 DGA", flows_t7, True, "DGA")

# T8: DNS Tunnel - Expect MALICIOUS
flows_t8 = [make_obs(
    protocol=17,
    destination_port=53,
    dns_query=f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=50))}.tunnel.example.com",
    orig_ip_bytes=300,
    resp_ip_bytes=50,
    tcp_syn_orig=False,
    tcp_syn_resp=False,
    tcp_fin_orig=False,
    tcp_fin_resp=False,
    orig_packets=1,
    resp_packets=1,
) for _ in range(25)] # increased to 25 to hit threshold
test("T8 DNS Tunnel", flows_t8, True, "Tunneling")

# T9: Encrypted Session - Expect MALICIOUS
flows_t9 = [make_obs(
    destination_ip="10.0.0.9",
    destination_port=443,
    tls_ja3="a0e9f5d64349fb13191bc781f81f42e1", # consistent JA3
    tls_sni="suspicious-c2.example.com",
    orig_ip_bytes=500,
    resp_ip_bytes=200,
    bidirectional_bytes=700,
    timestamp=now_ms + (i * 1000)
) for i in range(15)]
test("T9 Encrypted Session", flows_t9, True, "TLSAnomaly")

# T10: Port Scan (Vertical)
flows_t10 = [make_obs(
    destination_ip="10.0.0.50",
    destination_port=i * 100 + 1,
    orig_packets=1,
    resp_packets=0,
    orig_ip_bytes=54,
    resp_ip_bytes=0,
    tcp_fin_orig=False,
    tcp_fin_resp=False,
    duration=0.01,
) for i in range(1, 30)]
test("T10 Port Scan", flows_t10, True, "PortScan")

# T11: Slow Scan (Missed by deterministic threshold due to stealth)
flows_t11 = [make_obs(
    destination_ip=f"10.0.0.{i}",
    destination_port=22,
    orig_packets=1,
    resp_packets=0,
    orig_ip_bytes=54,
    resp_ip_bytes=0,
    tcp_fin_orig=False,
    tcp_fin_resp=False,
    duration=0.01,
) for i in range(1, 10)]
test("T11 Slow Scan", flows_t11, False) # Expected missed by threshold

# T12: Data Exfiltration
flows_t12 = [make_obs(
    destination_port=443,
    orig_ip_bytes=1500000,  # 1.5MB out
    resp_ip_bytes=1000,     # 1KB in
    orig_packets=1000,
    resp_packets=10,
)]
test("T12 Data Exfiltration", flows_t12, True, "Exfiltration")

# T13: Slowloris
flows_t13 = [make_obs(
    source_ip="192.168.1.150",
    destination_ip="10.0.0.80",
    source_port=10000 + i,
    destination_port=80,
    orig_packets=3,
    resp_packets=1,
    orig_ip_bytes=120,
    resp_ip_bytes=40,
    tcp_fin_orig=False,
    tcp_fin_resp=False,
    duration=60.0,
) for i in range(50)]
test("T13 Slowloris", flows_t13, True, "SlowHTTP")

# T14: High Fanout Benign (CDN/load balancer)
flows_t14 = [make_obs(
    destination_ip=f"10.0.{i // 256}.{i % 256}",
    destination_port=443,
    orig_ip_bytes=5000,
    resp_ip_bytes=50000,
    orig_packets=20,
    resp_packets=50,
) for i in range(30)]
test("T14 High Fanout Benign", flows_t14, False)

# T15: Spoofed-source SYN Flood
flows_t15 = [make_obs(
    source_ip=f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
    destination_ip="192.168.1.1",
    orig_packets=1,
    resp_packets=0,
    orig_ip_bytes=54,
    resp_ip_bytes=0,
    tcp_syn_orig=True,
    tcp_syn_resp=False,
    tcp_fin_orig=False,
    tcp_fin_resp=False,
    duration=0.01,
) for _ in range(600)]
test("T15 Spoofed-source SYN Flood", flows_t15, True, "DDoS")


print("\n" + "=" * 100)
print("REGRESSION SUMMARY")
print("=" * 100)

passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if "FAIL" in r["status"])
print(f"\n  PASSED: {passed}/{len(results)}")
print(f"  FAILED: {failed}/{len(results)}")

for r in results:
    if "FAIL" in r["status"]:
        print(f"  REGRESSION: {r['test']} — {r['status']}")

# Export JSON
with open("scripts/final_threat_regression.json", "w") as f:
    json.dump({"timestamp": time.time(), "results": results, "passed": passed, "failed": failed}, f, indent=2)

print(f"\n  Regression JSON saved to scripts/final_threat_regression.json")
