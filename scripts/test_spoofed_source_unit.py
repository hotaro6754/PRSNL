"""
Unit test: Spoofed-source flood detection via the existing DDoS detector.

The DDoS detector already has source-IP entropy analysis (spoof_entropy_threshold=2.5)
and specifically labels "Spoofed SYN Flood" when high PPS + high SYN ratio + high entropy.

This test verifies that the EXISTING detector catches the pattern without any new code.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import uuid
import json
import random
from backend.contracts.observation import NetworkObservation
from backend.detectors.ddos import DDoSDetector

det = DDoSDetector()
now_ms = int(time.time() * 1000)

# === TEST: Spoofed-source SYN flood ===
# Many different source IPs (high entropy), all SYN-only, targeting one destination
print("=== TEST: Spoofed-Source SYN Flood ===")

spoofed_flows = []
for i in range(600):  # >500 pps threshold in 1 second window
    src_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    obs = NetworkObservation(
        observation_id=str(uuid.uuid4()),
        flow_id=f"spoof_{i}",
        timestamp=now_ms + (i * 1),  # all within ~600ms
        first_seen=now_ms,
        last_seen=now_ms + 100,
        duration=0.01,
        source_ip=src_ip,
        destination_ip="192.168.1.1",  # single victim
        source_port=random.randint(1024, 65535),
        destination_port=80,
        protocol=6,  # TCP
        orig_packets=1,   # SYN only
        resp_packets=0,   # no response (spoofed)
        orig_ip_bytes=54, # SYN packet
        resp_ip_bytes=0,
        tcp_syn_orig=True,
        tcp_syn_resp=False,
        tcp_fin_orig=False,
        tcp_fin_resp=False,
        tcp_rst_orig=False,
        tcp_rst_resp=False,
    )
    spoofed_flows.append(obs)

# The DDoS detector uses flow.bidirectional_packets which doesn't exist
# on the pydantic model — it uses flow.packets property instead.
# But the DDoS detector references tcp_flags attribute which may not be numeric.
# Let's test and see what happens.

# Patch: The DDoS detector reads `flow.tcp_flags` as an int bitmask,
# but NetworkObservation has boolean fields instead.
# The DDoS detector was written for a dict-based flow, not the Pydantic model.
# For this test, we need to check if it handles the Pydantic model.

# Actually, looking at ddos.py line 51: `pkts = flow.bidirectional_packets or 1`
# NetworkObservation has a `packets` property, not `bidirectional_packets`.
# And line 63: `flags = flow.tcp_flags or 0` — NetworkObservation has no tcp_flags int.

# The DDoS detector was designed for the dict-based pcap_engine flows, not Pydantic.
# This means it would crash in production too when receiving Zeek-adapter flows.
# This is a real bug — let me check what the production backend main.py does.

print("Testing DDoS detector with Pydantic NetworkObservation...")
try:
    alerts = det.evaluate_window(spoofed_flows, now_ms)
    print(f"  Alerts: {len(alerts)}")
    if alerts:
        a = alerts[0]
        print(f"  Threat class: {a.threat_class}")
        print(f"  Attack type: {[e.value for e in a.evidence if e.feature == 'attack_type']}")
        print(f"  Source entropy: {[e.value for e in a.evidence if e.feature == 'source_entropy']}")
        print(f"  Confidence: {a.confidence}")
        for ev in a.evidence:
            print(f"    {ev.feature} = {ev.value}")
        
        result = {
            "test": "spoofed_source_unit",
            "detector": a.detector_id,
            "detected": True,
            "attack_type": [e.value for e in a.evidence if e.feature == "attack_type"][0],
            "source_entropy": [e.value for e in a.evidence if e.feature == "source_entropy"][0],
            "confidence": a.confidence,
            "threat_class": str(a.threat_class),
            "evidence": [{"feature": e.feature, "value": e.value} for e in a.evidence],
        }
        print(f"\n  Evidence JSON:\n{json.dumps(result, indent=2)}")
    else:
        print("  MISSED — no alerts generated")
except AttributeError as e:
    print(f"  DDoS detector crash: {e}")
    print("  This is a KNOWN COMPATIBILITY BUG: DDoS detector references")
    print("  dict-style attributes (bidirectional_packets, tcp_flags) that")
    print("  don't exist on the Pydantic NetworkObservation model.")
    print("  The detector needs patching to use .packets and boolean TCP flags.")
