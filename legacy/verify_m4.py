import os
import json
from backend.detectors.dga import DGADetector
from backend.detectors.dns_tunnel import DNSTunnelDetector
from backend.ingestion.scapy_adapter import ScapyAdapter

def run_verification():
    pcaps = [
        "data/pcaps/benign_dns.pcap",
        "data/pcaps/dga_botnet.pcap",
        "data/pcaps/dns_tunnel.pcap"
    ]
    
    print("--- M4 DNS/DGA/TUNNEL BASELINE VALIDATION ---")
    
    for pcap_file in pcaps:
        if not os.path.exists(pcap_file):
            print(f"Error: {pcap_file} not found.")
            continue
            
        print(f"\nEvaluating: {pcap_file}")
        
        dga_detector = DGADetector()
        tunnel_detector = DNSTunnelDetector()
        
        all_alerts = []
        
        adapter = ScapyAdapter()
        for flow in adapter.consume(pcap_file):
            all_alerts.extend(dga_detector.add_flow(flow))
            all_alerts.extend(tunnel_detector.add_flow(flow))
            
        all_alerts.extend(dga_detector.flush())
        all_alerts.extend(tunnel_detector.flush())
        
        if not all_alerts:
            print("  Result: 0 Alerts (Clean)")
        else:
            print(f"  Result: {len(all_alerts)} Alerts")
            for alert in all_alerts:
                print(f"    -> [ALERT] {alert.threat_class} | src: {alert.source_ip} | dst: {alert.destination_ip} | Confidence: {alert.confidence}")
                print(f"       Evidence: {json.dumps([e.model_dump() for e in alert.evidence])}")

if __name__ == "__main__":
    run_verification()
