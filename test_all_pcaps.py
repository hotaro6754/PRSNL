import os
import glob
from backend.ingestion.scapy_adapter import ScapyAdapter
from backend.detectors.ddos import DDoSDetector
from backend.detectors.scan import PortScanDetector
from backend.detectors.beacon import BeaconingDetector
from backend.detectors.dga import DGADetector
from backend.detectors.exfil import ExfiltrationDetector
from backend.detectors.tls_anomaly import TLSAnomalyDetector
from backend.detectors.brute_force import BruteForceDetector
import time

def test_all():
    pcaps = glob.glob('data/pcaps/*.pcap')
    detectors = [
        DDoSDetector(),
        PortScanDetector(),
        BeaconingDetector(),
        DGADetector(),
        ExfiltrationDetector(),
        TLSAnomalyDetector(),
        BruteForceDetector()
    ]
    
    total_alerts = 0
    for pcap in pcaps:
        print(f"\n--- Processing {pcap} ---")
        adapter = ScapyAdapter()
        flows = list(adapter.consume(pcap))
        
        # Simple window grouping (put everything in one window)
        current_time = int(time.time() * 1000)
        pcap_alerts = 0
        for detector in detectors:
            try:
                alerts = detector.evaluate_window(flows, current_time)
                for alert in alerts:
                    print(f"[{alert.threat_class}] Confidence: {alert.confidence} | SRC: {alert.source_ip}")
                    pcap_alerts += 1
            except Exception as e:
                print(f"Error in {detector.detector_id}: {e}")
                
        total_alerts += pcap_alerts
        if pcap_alerts == 0:
            print("No alerts triggered.")
            
    print(f"\nCompleted testing all {len(pcaps)} pcaps. Total Alerts: {total_alerts}")

if __name__ == '__main__':
    test_all()
