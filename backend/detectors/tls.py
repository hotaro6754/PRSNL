import math
import uuid
import time
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from collections import deque
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.contracts.observation import NetworkObservation
from backend.config import ThreatClass, Severity

class TLSSessionDetector(BaseDetector):
    def __init__(self, window_size_ms: int = 10000):
        super().__init__(window_size_ms=window_size_ms, detector_id="tls_behavioral_v1")
        
        # Bounded Temporal State
        # Key: (src_ip, dst_ip, dst_port)
        # Value: stream metadata
        self.state: Dict[Tuple, Dict[str, Any]] = {}
        self.ttl_ms = 3600 * 1000 # 1 hour
        
    def add_flow(self, flow: NetworkObservation) -> List[Alert]:
        alerts = super().add_flow(flow)
        
        src = flow.source_ip
        dst = flow.destination_ip
        port = flow.destination_port
        proto = flow.protocol
        ts = flow.timestamp
        
        # Focus on TCP/UDP standard encrypted ports or identified TLS flows
        tls_ja3 = flow.tls_ja3
        tls_sni = flow.tls_sni
        packet_size = flow.bidirectional_bytes or 0
        
        # We only track state for traffic that is either on 443, 853, etc, OR has a TLS fingerprint
        if not src or not dst or not ts:
            return alerts
            
        if port not in [443, 8443, 853] and not tls_ja3:
            return alerts
            
        key = (src, dst, port)
        
        if key not in self.state:
            self.state[key] = {
                "packet_sizes": deque(maxlen=20),
                "timestamps": deque(maxlen=20),
                "ja3_hashes": set(),
                "snis": set(),
                "total_bytes_out": 0,
                "total_bytes_in": 0,
                "last_seen": ts,
                "alerted": False
            }
            
        stream = self.state[key]
        stream["last_seen"] = ts
        stream["packet_sizes"].append(packet_size)
        stream["timestamps"].append(ts)
        
        if tls_ja3:
            stream["ja3_hashes"].add(tls_ja3)
        if tls_sni:
            stream["snis"].add(tls_sni)
            
        # Evaluate if we have enough packets
        if len(stream["packet_sizes"]) >= 10 and not stream["alerted"]:
            alerts.extend(self._evaluate_stream(key, stream, flow))
            
        self._garbage_collect(ts)
        return alerts

    def _evaluate_stream(self, key: Tuple, stream: Dict, flow: NetworkObservation) -> List[Alert]:
        alerts = []
        
        # Feature 1: Fingerprint Persistence
        # A single consistent JA3 hash is evidence. Multiple implies standard browser/OS updates.
        ja3_count = len(stream["ja3_hashes"])
        
        # Feature 2: Packet Size Variance
        # Browsing has high variance. C2 heartbeat has extremely low variance.
        sizes = list(stream["packet_sizes"])
        mean_size = np.mean(sizes)
        std_size = np.std(sizes)
        cv_size = std_size / mean_size if mean_size > 0 else 0.0
        
        # Feature 3: Periodicity (Jitter)
        timestamps = list(stream["timestamps"])
        iats = np.diff(timestamps)
        if len(iats) > 0:
            mean_iat = np.mean(iats)
            std_iat = np.std(iats)
            cv_iat = std_iat / mean_iat if mean_iat > 0 else 0.0
        else:
            cv_iat = 0.0
            
        # Detection Rule: Encrypted C2
        # Requires: consistent JA3 (if seen) + low packet size variance + low inter-arrival variance
        is_suspicious = False
        confidence = 0.0
        
        if cv_size < 0.1 and cv_iat < 0.2:
            is_suspicious = True
            confidence = 0.85
            # If JA3 is present and strictly consistent, boost confidence
            if ja3_count == 1:
                confidence += 0.1
                
        if is_suspicious:
            obs_score = self.calculate_observability(flow)
            
            ja3_evidence = list(stream["ja3_hashes"])[0] if ja3_count == 1 else "MULTIPLE/NONE"
            
            alerts.append(Alert(
                alert_id=uuid.uuid4(),
                timestamp=datetime.fromtimestamp(stream["last_seen"] / 1000.0, tz=timezone.utc),
                flow_id="encrypted_session_aggregate",
                source_ip=key[0],
                destination_ip=key[1],
                protocol="TCP/UDP",
                threat_class=ThreatClass.TLSAnomaly, # Encrypted Session behavior
                detector_id=self.detector_id,
                severity=Severity.HIGH,
                confidence=min(0.95, confidence) * obs_score,
                observability_score=obs_score,
                evidence=[
                    EvidenceItem(feature="ja3_hash", value=ja3_evidence, contribution=0.3),
                    EvidenceItem(feature="packet_size_cv", value=round(cv_size, 3), contribution=0.4),
                    EvidenceItem(feature="inter_arrival_cv", value=round(cv_iat, 3), contribution=0.3)
                ]
            ))
            stream["alerted"] = True
            
        return alerts

    def _garbage_collect(self, current_time_ms: float = None):
        current_time = current_time_ms if current_time_ms else (time.time() * 1000)
        expired_keys = []
        for k, v in self.state.items():
            if current_time - v["last_seen"] > self.ttl_ms:
                expired_keys.append(k)
        for k in expired_keys:
            del self.state[k]

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        alerts = []
        for flow in flows:
            src = flow.source_ip
            dst = flow.destination_ip
            port = flow.destination_port
            proto = flow.protocol
            ts = flow.timestamp
            
            tls_ja3 = flow.tls_ja3
            tls_sni = flow.tls_sni
            packet_size = flow.bidirectional_bytes or 0
            
            if not src or not dst or not ts:
                continue
                
            if port not in [443, 8443, 853] and not tls_ja3:
                continue
                
            key = (src, dst, port)
            
            if key not in self.state:
                self.state[key] = {
                    "packet_sizes": deque(maxlen=20),
                    "timestamps": deque(maxlen=20),
                    "ja3_hashes": set(),
                    "snis": set(),
                    "total_bytes_out": 0,
                    "total_bytes_in": 0,
                    "last_seen": ts,
                    "alerted": False
                }
                
            stream = self.state[key]
            stream["last_seen"] = ts
            stream["packet_sizes"].append(packet_size)
            stream["timestamps"].append(ts)
            
            if tls_ja3:
                stream["ja3_hashes"].add(tls_ja3)
            if tls_sni:
                stream["snis"].add(tls_sni)
                
            if len(stream["packet_sizes"]) >= 10 and not stream["alerted"]:
                alerts.extend(self._evaluate_stream(key, stream, flow))
                
        self._garbage_collect(window_start_ms)
        return alerts

