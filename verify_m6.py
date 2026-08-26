import os
import json
from backend.detectors.tls import TLSSessionDetector
from backend.ingestion.scapy_adapter import ScapyAdapter

def run_verification():
    pcaps = [
        "data/pcaps/benign_https.pcap",
        "data/pcaps/benign_api.pcap",
        "data/pcaps/encrypted_c2.pcap",
        "data/pcaps/jittered_encrypted_c2.pcap"
    ]
    
    print("--- M6 ENCRYPTED SESSION BASELINE VALIDATION ---")
    
    for pcap_file in pcaps:
        if not os.path.exists(pcap_file):
            print(f"Error: {pcap_file} not found.")
            continue
            
        print(f"\nEvaluating: {pcap_file}")
        
        detector = TLSSessionDetector()
        
        all_alerts = []
        
        adapter = ScapyAdapter()
        for flow in adapter.consume(pcap_file):
            all_alerts.extend(detector.add_flow(flow))
            
        all_alerts.extend(detector.flush())
        
        if not all_alerts:
            print("  Result: 0 Alerts (Clean)")
        else:
            # We evaluate streams at flow 10, so it might alert multiple times on the same stream for flows 11-15.
            # Let's deduplicate for display based on alert.threat_class + src + dst
            unique_alerts = {}
            for alert in all_alerts:
                key = (alert.threat_class, alert.source_ip, alert.destination_ip)
                if key not in unique_alerts:
                    unique_alerts[key] = alert
                    
            print(f"  Result: {len(unique_alerts)} Unique Alerts")
            for alert in unique_alerts.values():
                print(f"    -> [ALERT] {alert.threat_class} | src: {alert.source_ip} | dst: {alert.destination_ip} | Confidence: {alert.confidence}")
                print(f"       Evidence: {json.dumps([e.model_dump() for e in alert.evidence])}")

if __name__ == "__main__":
    run_verification()
