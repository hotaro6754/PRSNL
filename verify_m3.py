import os
import json
from backend.detectors.beacon import BeaconingDetector
from backend.ingestion.scapy_adapter import ScapyAdapter

def run_verification():
    pcaps = [
        "data/pcaps/ntp_polling.pcap",
        "data/pcaps/api_polling.pcap",
        "data/pcaps/rigid_beacon.pcap",
        "data/pcaps/jittered_beacon.pcap",
        "data/pcaps/slow_beacon.pcap"
    ]
    
    print("--- M3 BEACONING BASELINE VALIDATION ---")
    
    for pcap_file in pcaps:
        if not os.path.exists(pcap_file):
            print(f"Error: {pcap_file} not found.")
            continue
            
        print(f"\nEvaluating: {pcap_file}")
        
        # Detector with internal state
        detector = BeaconingDetector(window_size_ms=10000)
        all_alerts = []
        
        adapter = ScapyAdapter()
        for flow in adapter.consume(pcap_file):
            alerts = detector.add_flow(flow)
            all_alerts.extend(alerts)
            
        # Standard flush does nothing in the new architecture, but we call it anyway
        all_alerts.extend(detector.flush())
        
        if not all_alerts:
            print("  Result: 0 Alerts (Clean)")
        else:
            print(f"  Result: {len(all_alerts)} Alerts")
            for alert in all_alerts:
                print(f"    -> [ALERT] {alert.threat_class} | src: {alert.source_ip} | dst: {alert.destination_ip} | Confidence: {alert.confidence}")
                print(f"       Evidence: {json.dumps([e.model_dump() for e in alert.evidence])}")

if __name__ == "__main__":
    run_verification()
