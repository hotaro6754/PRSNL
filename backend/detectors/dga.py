from backend.contracts.observation import NetworkObservation
import math
import uuid
import re
from typing import List, Optional
from datetime import datetime, timezone
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.config import ThreatClass, Severity

class DGADetector(BaseDetector):
    def __init__(self, window_size_ms: int = 1000):
        # We can evaluate inline, so window size doesn't strictly matter
        super().__init__(window_size_ms=window_size_ms, detector_id="dga_lexical_v1")
        self.seen_domains = set() # Prevent alert spam for the same domain
        
        # M4 Heuristics
        self.entropy_threshold = 3.8
        self.consonant_ratio_threshold = 0.75
        self.digit_ratio_threshold = 0.4
        self.max_length_threshold = 30

    def get_sld(self, domain: str) -> str:
        """Extracts the Second-Level Domain (e.g. 'google' from 'www.google.com')."""
        parts = domain.split('.')
        if len(parts) >= 2:
            return parts[-2]
        return domain

    def calculate_entropy(self, text: str) -> float:
        if not text: return 0.0
        counts = {}
        for char in text:
            counts[char] = counts.get(char, 0) + 1
        entropy = 0.0
        total = len(text)
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        alerts = []
        if not flows:
            return alerts

        for flow in flows:
            domain = flow.dns_query
            if not domain or domain in self.seen_domains:
                continue

            self.seen_domains.add(domain)
            sld = self.get_sld(domain)
            if not sld:
                continue
                
            entropy = self.calculate_entropy(sld)
            length = len(sld)
            
            # Character distribution
            consonants = sum(1 for c in sld if c.isalpha() and c.lower() not in 'aeiou')
            digits = sum(1 for c in sld if c.isdigit())
            
            consonant_ratio = consonants / max(1, length)
            digit_ratio = digits / max(1, length)
            
            is_dga = False
            confidence = 0.0
            
            # Legitimate CDNs often have high entropy but mix alphanumeric (e.g., a1b2c3d4).
            # Conficker-style DGA is often just consonant-heavy random letters (kxjhqzv).
            # Cryptolocker-style DGA can be long strings.
            
            # Rule 1: High Entropy + High Consonant Ratio (Pure letter DGA)
            if entropy > self.entropy_threshold and consonant_ratio > self.consonant_ratio_threshold:
                is_dga = True
                confidence = 0.85
                
            # Rule 2: High Digit Ratio + High Entropy (Alphanumeric DGA)
            elif entropy > self.entropy_threshold and digit_ratio > self.digit_ratio_threshold:
                is_dga = True
                confidence = 0.80
                
            # Rule 3: Extreme Length + High Entropy
            elif length > self.max_length_threshold and entropy > 3.0:
                is_dga = True
                confidence = 0.75
                
            # Rule 4: Pure Consonants (Catches short Conficker-like DGAs with low entropy)
            elif consonant_ratio > 0.95 and length >= 10:
                is_dga = True
                confidence = 0.85
                
            if is_dga:
                obs_score = self.calculate_observability(flow)
                alerts.append(Alert(
                    alert_id=uuid.uuid4(),
                    timestamp=datetime.fromtimestamp((flow.timestamp or 0) / 1000.0, tz=timezone.utc),
                    flow_id=flow.flow_id,
                    source_ip=flow.source_ip,
                    destination_ip=flow.destination_ip,
                    protocol="UDP",
                    threat_class=ThreatClass.DGA,
                    detector_id=self.detector_id,
                    severity=Severity.HIGH,
                    confidence=confidence * obs_score,
                    observability_score=obs_score,
                    evidence=[
                        EvidenceItem(feature="dns_query", value=domain, contribution=0.4),
                        EvidenceItem(feature="sld_entropy", value=round(entropy, 2), contribution=0.3),
                        EvidenceItem(feature="consonant_ratio", value=round(consonant_ratio, 2), contribution=0.15),
                        EvidenceItem(feature="digit_ratio", value=round(digit_ratio, 2), contribution=0.15)
                    ]
                ))
                
        return alerts
