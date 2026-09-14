from backend.contracts.observation import NetworkObservation
import uuid
from typing import List
from datetime import datetime, timezone
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.config import ThreatClass, Severity
from collections import defaultdict

class BruteForceDetector(BaseDetector):
    def __init__(self, window_size_ms: int = 10000):
        # 10 second window
        super().__init__(window_size_ms=window_size_ms, detector_id="bruteforce_v1")
        self.target_ports = {22, 21, 3389, 1433, 3306}
        self.attempt_threshold = 15

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        if not flows:
            return []

        # src_ip -> dst_ip -> port -> list of flows
        attempts = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for flow in flows:
            if flow.protocol == 6 and flow.destination_port in self.target_ports:
                if flow.source_ip and flow.destination_ip:
                    attempts[flow.source_ip][flow.destination_ip][flow.destination_port].append(flow)

        alerts = []
        for src, dsts in attempts.items():
            for dst, ports in dsts.items():
                for port, port_flows in ports.items():
                    if len(port_flows) >= self.attempt_threshold:
                        # Check if these are short flows
                        total_bytes = sum((f.bidirectional_bytes or 0) for f in port_flows)
                        avg_bytes = total_bytes / len(port_flows)
                        
                        if avg_bytes < 8000: # Typical brute force attempt is small
                            sample_flow = port_flows[0]
                            obs_score = self.calculate_observability(sample_flow)
                            
                            alerts.append(Alert(
                                alert_id=uuid.uuid4(),
                                timestamp=datetime.fromtimestamp(window_start_ms / 1000.0, tz=timezone.utc),
                                flow_id="bruteforce_aggregate",
                                source_ip=src,
                                destination_ip=dst,
                                protocol="TCP",
                                threat_class=ThreatClass.BruteForce,
                                detector_id=self.detector_id,
                                severity=Severity.HIGH,
                                confidence=0.90 * obs_score,
                                observability_score=obs_score,
                                evidence=[
                                    EvidenceItem(feature="target_port", value=port, contribution=0.4),
                                    EvidenceItem(feature="attempt_count", value=len(port_flows), contribution=0.4),
                                    EvidenceItem(feature="avg_bytes_per_attempt", value=round(avg_bytes, 2), contribution=0.2)
                                ]
                            ))

        return alerts
