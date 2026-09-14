from backend.contracts.observation import NetworkObservation
from typing import List, Dict
import logging
import uuid
from datetime import datetime, timezone
from backend.detectors.base import BaseDetector
from backend.schemas import Alert, EvidenceItem
from backend.config import ThreatClass, Severity
from backend.features.tls_features import tls_flow_features, load_malicious_ja3_set

logger = logging.getLogger(__name__)

class TLSAnomalyDetector(BaseDetector):
    def __init__(self, window_size_ms: int = 60000, name: str = "tls_anomaly_v1"):
        super().__init__(window_size_ms=window_size_ms, detector_id=name)
        self.malicious_ja3 = load_malicious_ja3_set("")

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        alerts = []
        for flow in flows:
            # Observability defaults to 1.0, lower if bidirectional flow is missing
            obs_score = self.calculate_observability(flow)
            features = tls_flow_features(flow)
            ja3 = features.get("client_fingerprint")
            sni = features.get("requested_server_name")
            
            # JA3 Match
            if ja3 and ja3 in self.malicious_ja3:
                alerts.append(Alert(
                    alert_id=uuid.uuid4(),
                    timestamp=datetime.fromtimestamp(flow.get("bidirectional_first_seen_ms", window_start_ms) / 1000.0, tz=timezone.utc),
                    flow_id=f"{flow.get('src_ip')}:{flow.get('src_port')} -> {flow.get('dst_ip')}:{flow.get('dst_port')}",
                    source_ip=flow.get("src_ip", "UNKNOWN"),
                    destination_ip=flow.get("dst_ip", "UNKNOWN"),
                    protocol=str(flow.get("protocol", "UNKNOWN")),
                    threat_class=ThreatClass.TLSAnomaly,
                    detector_id=self.detector_id,
                    severity=Severity.CRITICAL,
                    confidence=0.95 * obs_score,
                    observability_score=obs_score,
                    evidence=[
                        EvidenceItem(feature="matched_ja3", value=ja3, contribution=0.9),
                        EvidenceItem(feature="sni", value=sni, contribution=0.1)
                    ]
                ))
            
            # Unusually small flow but TLS (possible C2 beaconing using TLS)
            elif not ja3 and features["packet_count"] < 15 and features["duration"] > 5000:
                 alerts.append(Alert(
                    alert_id=uuid.uuid4(),
                    timestamp=datetime.fromtimestamp(flow.get("bidirectional_first_seen_ms", window_start_ms) / 1000.0, tz=timezone.utc),
                    flow_id=f"{flow.get('src_ip')}:{flow.get('src_port')} -> {flow.get('dst_ip')}:{flow.get('dst_port')}",
                    source_ip=flow.get("src_ip", "UNKNOWN"),
                    destination_ip=flow.get("dst_ip", "UNKNOWN"),
                    protocol=str(flow.get("protocol", "UNKNOWN")),
                    threat_class=ThreatClass.TLSAnomaly,
                    detector_id=self.detector_id,
                    severity=Severity.MEDIUM,
                    confidence=0.6 * obs_score,
                    observability_score=obs_score,
                    evidence=[
                        EvidenceItem(feature="packet_count", value=features["packet_count"], contribution=0.5),
                        EvidenceItem(feature="duration_ms", value=features["duration"], contribution=0.5)
                    ]
                ))

        return alerts
