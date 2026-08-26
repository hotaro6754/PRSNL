from typing import List, Dict, Any, Tuple, Optional
import uuid
from datetime import datetime, timezone
import time
from collections import deque
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.contracts.observation import NetworkObservation
from backend.config import ThreatClass, Severity

class DNSTunnelDetector(BaseDetector):
    def __init__(self, window_size_ms: int = 10000):
        super().__init__(window_size_ms=window_size_ms, detector_id="dns_tunnel_stateful_v1")
        
        # Bounded Temporal State
        # Key: (src_ip, root_domain)
        # Value: dict with 'queries' (set of unique subdomains), 'total_payload_bytes', 'last_seen', 'count'
        self.state: Dict[Tuple, Dict[str, Any]] = {}
        
        self.max_unique_subdomains = 20 # Threshold for tunnelling suspicion
        self.min_payload_bytes = 1000 # Minimum total length of subdomains to be considered exfiltration/tunnelling
        self.ttl_ms = 3600 * 1000  # 1 hour TTL
        
    def get_root_domain(self, domain: str) -> str:
        """Extracts the root domain (e.g. 'tunnel.com' from 'data.tunnel.com')."""
        parts = domain.split('.')
        if len(parts) >= 2:
            return f"{parts[-2]}.{parts[-1]}"
        return domain

    def add_flow(self, flow: NetworkObservation) -> List[Alert]:
        alerts = super().add_flow(flow)
        
        domain = flow.dns_query
        src = flow.source_ip
        ts = flow.timestamp
        
        if src and domain and ts:
            root_domain = self.get_root_domain(domain)
            key = (src, root_domain)
            
            if key not in self.state:
                self.state[key] = {
                    "unique_subdomains": set(),
                    "total_payload_bytes": 0,
                    "last_seen": ts,
                    "alerted": False,
                    "query_count": 0
                }
                
            stream = self.state[key]
            stream["last_seen"] = ts
            stream["query_count"] += 1
            
            # Extract the subdomain part (the payload)
            subdomain = domain[:-(len(root_domain)+1)] if domain.endswith(f".{root_domain}") else ""
            
            if subdomain and subdomain not in stream["unique_subdomains"]:
                # To prevent memory unboundedness, we bound the set at max threshold + 10
                if len(stream["unique_subdomains"]) < self.max_unique_subdomains + 10:
                    stream["unique_subdomains"].add(subdomain)
                    stream["total_payload_bytes"] += len(subdomain)
                    
            if not stream["alerted"] and len(stream["unique_subdomains"]) >= self.max_unique_subdomains:
                if stream["total_payload_bytes"] >= self.min_payload_bytes:
                    alert = self._generate_alert(key, stream, flow)
                    alerts.append(alert)
                    stream["alerted"] = True
                    
        self._garbage_collect(ts)
        return alerts

    def _garbage_collect(self, current_time_ms: float = None):
        current_time = current_time_ms if current_time_ms else (time.time() * 1000)
        expired_keys = []
        for k, v in self.state.items():
            if current_time - v["last_seen"] > self.ttl_ms:
                expired_keys.append(k)
        for k in expired_keys:
            del self.state[k]

    def _generate_alert(self, key: Tuple, stream: Dict, flow: NetworkObservation) -> Alert:
        obs_score = self.calculate_observability(flow)
        return Alert(
            alert_id=uuid.uuid4(),
            timestamp=datetime.fromtimestamp(stream["last_seen"] / 1000.0, tz=timezone.utc),
            flow_id="dns_tunnel_aggregate",
            source_ip=key[0],
            destination_ip="MULTIPLE",
            protocol="UDP",
            threat_class=ThreatClass.Tunneling,
            detector_id=self.detector_id,
            severity=Severity.CRITICAL,
            confidence=0.90 * obs_score,
            observability_score=obs_score,
            evidence=[
                EvidenceItem(feature="root_domain", value=key[1], contribution=0.4),
                EvidenceItem(feature="unique_subdomains", value=len(stream["unique_subdomains"]), contribution=0.3),
                EvidenceItem(feature="total_payload_bytes", value=stream["total_payload_bytes"], contribution=0.3)
            ]
        )

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        alerts = []
        for flow in flows:
            domain = flow.dns_query
            src = flow.source_ip
            ts = flow.timestamp
            
            if src and domain and ts:
                root_domain = self.get_root_domain(domain)
                key = (src, root_domain)
                
                if key not in self.state:
                    self.state[key] = {
                        "unique_subdomains": set(),
                        "total_payload_bytes": 0,
                        "last_seen": ts,
                        "alerted": False,
                        "query_count": 0
                    }
                    
                stream = self.state[key]
                stream["last_seen"] = ts
                stream["query_count"] += 1
                
                subdomain = domain[:-(len(root_domain)+1)] if domain.endswith(f".{root_domain}") else ""
                
                if subdomain and subdomain not in stream["unique_subdomains"]:
                    if len(stream["unique_subdomains"]) < self.max_unique_subdomains + 10:
                        stream["unique_subdomains"].add(subdomain)
                        stream["total_payload_bytes"] += len(subdomain)
                        
                if not stream["alerted"] and len(stream["unique_subdomains"]) >= self.max_unique_subdomains:
                    if stream["total_payload_bytes"] >= self.min_payload_bytes:
                        alert = self._generate_alert(key, stream, flow)
                        alerts.append(alert)
                        stream["alerted"] = True
                        
        self._garbage_collect(window_start_ms)
        return alerts

