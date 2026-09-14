import os
import json
from backend.detectors.scan import PortScanDetector
from backend.ingestion.scapy_adapter import ScapyAdapter

def run_verification():
    pcaps = [
        "data/pcaps/benign_web.pcap",
        "data/pcaps/stealth_scan.pcap",
        "data/pcaps/mixed_noise.pcap"
    ]
    
    print("--- M1.5 ADVERSARIAL VALIDATION ---")
    
    for pcap_file in pcaps:
        if not os.path.exists(pcap_file):
            print(f"Error: {pcap_file} not found.")
            continue
            
        print(f"\nEvaluating: {pcap_file}")
        
        # We only care about the PortScanDetector for this test
        detector = PortScanDetector()
        all_alerts = []
        
        adapter = ScapyAdapter()
        for flow in adapter.consume(pcap_file):
            alerts = detector.add_flow(flow)
            all_alerts.extend(alerts)
            
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
