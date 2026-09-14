from typing import List, Dict, Any, Tuple, Optional
import uuid
import numpy as np
from datetime import datetime, timezone
import time
from collections import deque
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.contracts.observation import NetworkObservation
from backend.config import ThreatClass, Severity

class BeaconingDetector(BaseDetector):
    def __init__(self, window_size_ms: int = 10000):
        # The window size is for standard BaseDetector operations, 
        # but our state persists outside of it.
        super().__init__(window_size_ms=window_size_ms, detector_id="beacon_stateful_v2")
        
        # Bounded Temporal State
        # Key: (src_ip, dst_ip, dst_port, protocol)
        # Value: dict with 'timestamps' (deque) and 'bytes' (deque), and 'last_seen'
        self.state: Dict[Tuple, Dict[str, Any]] = {}
        
        self.max_history = 20
        self.min_flows_required = 5
        self.ttl_ms = 3600 * 1000  # 1 hour TTL for garbage collection
        
        # Heuristics
        self.max_jitter_cv = 0.5  # Accommodates up to 50% jitter
        self.min_period_ms = 1000 # Ignore things faster than 1s (likely not C2, more like a transfer)
        self.max_byte_cv = 0.2    # C2 beacons usually have very consistent payload sizes

    def add_flow(self, flow: NetworkObservation) -> List[Alert]:
        alerts = super().add_flow(flow)
        
        # Update Temporal State immediately as flows arrive
        src = flow.source_ip
        dst = flow.destination_ip
        port = flow.destination_port
        proto = flow.protocol
        ts = flow.timestamp
        b_bytes = flow.bidirectional_bytes or 0
        
        if src and dst and ts:
            key = (src, dst, port, proto)
            if key not in self.state:
                self.state[key] = {
                    "timestamps": deque(maxlen=self.max_history),
                    "bytes": deque(maxlen=self.max_history),
                    "last_seen": ts,
                    "alerted": False
                }
            
            # Avoid duplicate timestamps for the same flow key in the same millisecond
            if not self.state[key]["timestamps"] or self.state[key]["timestamps"][-1] != ts:
                self.state[key]["timestamps"].append(ts)
                self.state[key]["bytes"].append(b_bytes)
                self.state[key]["last_seen"] = ts
                
                # Check for beaconing inline since state crosses windows
                if not self.state[key]["alerted"] and len(self.state[key]["timestamps"]) >= self.min_flows_required:
                    alert = self._evaluate_stream(key, self.state[key], flow)
                    if alert:
                        alerts.append(alert)
                        self.state[key]["alerted"] = True # Prevent alert spam for this stream
                        
        self._garbage_collect(ts)
        return alerts
        
    def _garbage_collect(self, current_time_ms: float = None):
        """Purge inactive streams to prevent OOM."""
        current_time = current_time_ms if current_time_ms else (time.time() * 1000)
        expired_keys = []
        for k, v in self.state.items():
            if current_time - v["last_seen"] > self.ttl_ms:
                expired_keys.append(k)
        for k in expired_keys:
            del self.state[k]

    def _evaluate_stream(self, key: Tuple, stream_data: Dict, sample_flow: Optional[NetworkObservation]) -> Alert:
        timestamps = list(stream_data["timestamps"])
        bytes_list = list(stream_data["bytes"])
        
        iats = np.diff(timestamps)
        if len(iats) < 2:
            return None
            
        mean_iat = np.mean(iats)
        if mean_iat < self.min_period_ms:
            return None # Too fast, likely a burst transfer, not a beacon
            
        std_iat = np.std(iats)
        cv_iat = std_iat / mean_iat if mean_iat > 0 else 0
        
        mean_bytes = np.mean(bytes_list)
        std_bytes = np.std(bytes_list)
        cv_bytes = std_bytes / mean_bytes if mean_bytes > 0 else 0
        
        # Periodic Behavior Detection
        if cv_iat <= self.max_jitter_cv:
            # Benign Whitelist / Context Check
            port = key[2]
            if port == 123 and cv_iat < 0.05:
                # NTP is highly rigid. Do not alert.
                return None
                
            if cv_bytes > self.max_byte_cv:
                # Highly variable payload size usually indicates benign API polling
                return None
                
            obs_score = self.calculate_observability(sample_flow)
            
            # Confidence based on jitter tightness and flow count
            # More rigid = higher confidence. More flows = higher confidence.
            conf_base = 0.9 if cv_iat < 0.1 else 0.75
            confidence = conf_base * obs_score
            
            return Alert(
                alert_id=uuid.uuid4(),
                timestamp=datetime.fromtimestamp(timestamps[-1] / 1000.0, tz=timezone.utc),
                flow_id="beacon_stateful",
                source_ip=key[0],
                destination_ip=key[1],
                protocol=str(key[3]),
                threat_class=ThreatClass.Beaconing,
                detector_id=self.detector_id,
                severity=Severity.HIGH,
                confidence=confidence,
                observability_score=obs_score,
                evidence=[
                    EvidenceItem(feature="flow_count", value=len(timestamps), contribution=0.3),
                    EvidenceItem(feature="mean_interval_sec", value=round(mean_iat/1000.0, 2), contribution=0.3),
                    EvidenceItem(feature="jitter_cv", value=round(cv_iat, 3), contribution=0.2),
                    EvidenceItem(feature="byte_cv", value=round(cv_bytes, 3), contribution=0.2)
                ]
            )
        return None

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        alerts = []
        for flow in flows:
            src = flow.source_ip
            dst = flow.destination_ip
            port = flow.destination_port
            proto = flow.protocol
            ts = flow.timestamp
            b_bytes = flow.bidirectional_bytes or 0
            
            if src and dst and ts:
                key = (src, dst, port, proto)
                if key not in self.state:
                    self.state[key] = {
                        "timestamps": deque(maxlen=self.max_history),
                        "bytes": deque(maxlen=self.max_history),
                        "last_seen": ts,
                        "alerted": False
                    }
                
                if not self.state[key]["timestamps"] or self.state[key]["timestamps"][-1] != ts:
                    self.state[key]["timestamps"].append(ts)
                    self.state[key]["bytes"].append(b_bytes)
                    self.state[key]["last_seen"] = ts
                    
                    if not self.state[key]["alerted"] and len(self.state[key]["timestamps"]) >= self.min_flows_required:
                        alert = self._evaluate_stream(key, self.state[key], flow)
                        if alert:
                            alerts.append(alert)
                            self.state[key]["alerted"] = True
                            
        self._garbage_collect(window_start_ms)
        return alerts

