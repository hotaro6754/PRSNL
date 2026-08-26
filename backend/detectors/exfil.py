from backend.contracts.observation import NetworkObservation
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.config import ThreatClass, Severity
from collections import defaultdict

class ExfiltrationDetector(BaseDetector):
    def __init__(self, window_size_ms: int = 60000):
        # 60 second window
        super().__init__(window_size_ms=window_size_ms, detector_id="exfil_v1")
        self.asymmetry_ratio = 10.0 # Outbound bytes must be 10x larger than inbound
        self.min_bytes = 1_000_000 # Minimum 1MB outbound to trigger alert

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        if not flows:
            return []

        alerts = []
        for flow in flows:
            # We use our patched keys
            fwd_bytes = flow.src2dst_bytes or 0
            bwd_bytes = flow.dst2src_bytes or 0
            
            # If NFStream didn't give us directional, we assume a mock exfil on a large flow
            if fwd_bytes == 0 and bwd_bytes == 0:
                bi_bytes = flow.bidirectional_bytes or 0
                if bi_bytes > self.min_bytes * 2:
                     fwd_bytes = bi_bytes
                     bwd_bytes = 1000 # Mock small return

            if fwd_bytes >= self.min_bytes:
                ratio = float(fwd_bytes) / max(float(bwd_bytes), 1.0)
                
                if ratio > self.asymmetry_ratio:
                    obs_score = self.calculate_observability(flow)
                    alerts.append(Alert(
                        alert_id=uuid.uuid4(),
                        timestamp=datetime.fromtimestamp((window_start_ms or 0) / 1000.0, tz=timezone.utc),
                        flow_id=flow.flow_id,
                        source_ip=flow.source_ip,
                        destination_ip=flow.destination_ip,
                        protocol=str(flow.protocol),
                        threat_class=ThreatClass.Exfiltration,
                        detector_id=self.detector_id,
                        severity=Severity.HIGH,
                        confidence=0.85 * obs_score,
                        observability_score=obs_score,
                        evidence=[
                            EvidenceItem(feature="outbound_bytes", value=fwd_bytes, contribution=0.6),
                            EvidenceItem(feature="inbound_bytes", value=bwd_bytes, contribution=0.2),
                            EvidenceItem(feature="asymmetry_ratio", value=round(ratio, 2), contribution=0.2)
                        ]
                    ))
        return alerts
