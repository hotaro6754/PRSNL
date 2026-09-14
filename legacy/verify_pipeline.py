import asyncio
import os
import json
from backend.ingestion.scapy_adapter import ScapyAdapter
from backend.detectors.ddos import DDoSDetector
from backend.detectors.scan import PortScanDetector
from backend.detectors.beacon import BeaconingDetector
from backend.detectors.dga import DGADetector
from backend.detectors.exfil import ExfiltrationDetector
from backend.detectors.tls_anomaly import TLSAnomalyDetector

def verify_pipeline():
    print("Initializing Detectors...")
    detectors = [
        DDoSDetector(),
        PortScanDetector(),
        BeaconingDetector(),
        DGADetector(),
        ExfiltrationDetector(),
        TLSAnomalyDetector()
    ]
    
    pcap_file = "data/pcaps/real_port_scan.pcap"
    if not os.path.exists(pcap_file):
        print(f"Error: {pcap_file} not found.")
        return
        
    print(f"Replaying PCAP: {pcap_file}")
    
    total_alerts = 0
    adapter = ScapyAdapter()
    
    from backend.ml.feature_engine import TumblingWindowFeatureEngine
    from backend.ml.router import ModelRouter, EvidenceFusionEngine
    
    feature_engine = TumblingWindowFeatureEngine()
    
    from backend.ml.registry import ModelRegistry
    from backend.ml.resolver import ModelResolver
    # Mock or real
    try:
        registry = ModelRegistry('mongodb://localhost:27017')
        resolver = ModelResolver(registry, 'models')
        import asyncio
        asyncio.run(resolver.sync_models())
        model_router = ModelRouter(resolver)
    except:
        model_router = None

    fusion_engine = EvidenceFusionEngine()
    
    for flow in adapter.consume(pcap_file):
        det_alerts = []
        for detector in detectors:
            det_alerts.extend(detector.add_flow(flow))
            
        feature_engine.ingest(flow)
        fv = feature_engine.extract_features(flow.source_ip, flow.timestamp)
        ml_pred = None
        if fv:
            ml_pred = model_router.evaluate(fv, flow) if model_router else None
            
        final_alerts = fusion_engine.fuse(det_alerts, ml_pred, flow)
            
        for alert in final_alerts:
            total_alerts += 1
            print(f"\n[ALERT {total_alerts}] {alert.threat_category if hasattr(alert, 'threat_category') else getattr(alert, 'threat_class', 'UNKNOWN')} | Confidence: {alert.confidence:.2f}")
            print(f"  Source IP: {alert.source_ip}")
            print(f"  Evidence: {json.dumps([e.model_dump() for e in alert.evidence])}")
                
    for detector in detectors:
        alerts = detector.flush()
        for alert in alerts:
            total_alerts += 1
            print(f"\n[ALERT {total_alerts}] {alert.threat_category if hasattr(alert, 'threat_category') else getattr(alert, 'threat_class', 'UNKNOWN')} | Confidence: {alert.confidence:.2f}")
            print(f"  Source IP: {alert.source_ip}")
            print(f"  Evidence: {json.dumps([e.model_dump() for e in alert.evidence])}")

    print(f"\nVerification Complete. Total Alerts: {total_alerts}")

if __name__ == "__main__":
    verify_pipeline()
