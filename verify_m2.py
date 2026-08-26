import os
import json
from backend.detectors.ddos import DDoSDetector
from backend.ingestion.scapy_adapter import ScapyAdapter

def run_verification():
    pcaps = [
        "data/pcaps/benign_transfer.pcap",
        "data/pcaps/syn_flood.pcap",
        "data/pcaps/udp_flood.pcap"
    ]
    
    print("--- M2 DDoS BASELINE VALIDATION ---")
    
    for pcap_file in pcaps:
        if not os.path.exists(pcap_file):
            print(f"Error: {pcap_file} not found.")
            continue
            
        print(f"\nEvaluating: {pcap_file}")
        
        # 1-second window for DDoS evaluation
        detector = DDoSDetector(window_size_ms=1000)
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
