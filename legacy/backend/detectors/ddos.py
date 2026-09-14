from backend.contracts.observation import NetworkObservation
import uuid
import logging
from typing import List
from datetime import datetime, timezone
import math
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.config import ThreatClass, Severity

logger = logging.getLogger(__name__)

class DDoSDetector(BaseDetector):
    def __init__(self, window_size_ms: int = 1000):
        # 1 second window
        super().__init__(window_size_ms=window_size_ms, detector_id="ddos_stat_v1")
        
        # M2 Baseline Thresholds
        self.pps_threshold = 500  # Packets per second to trigger analysis
        self.bps_threshold = 10_000_000 # 10 Mbps
        self.syn_ratio_threshold = 0.8
        self.spoof_entropy_threshold = 2.5 # Shannon entropy of source IPs

    def calculate_entropy(self, items: List[str]) -> float:
        if not items: return 0.0
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        entropy = 0.0
        total = len(items)
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        if not flows:
            return []

        # Calculate metrics for the tumbling window
        total_packets = 0
        total_bytes = 0
        total_syn = 0
        total_udp = 0
        total_tcp = 0
        src_ips = []
        dst_ip = None # For volumetric, usually focused on one target in the window
        
        for flow in flows:
            pkts = flow.packets or 1
            b_bytes = flow.bidirectional_bytes or 0
            total_packets += pkts
            total_bytes += b_bytes
            
            src = flow.source_ip
            if src: src_ips.append(src)
            if not dst_ip: dst_ip = flow.destination_ip
            
            proto = flow.protocol or 0
            if proto == 6: # TCP
                total_tcp += pkts
                # Use boolean TCP flag fields from NetworkObservation
                if flow.tcp_syn_orig and not flow.tcp_syn_resp:
                    total_syn += pkts
            elif proto == 17: # UDP
                total_udp += pkts

        # Time normalization
        if flows:
            max_ts = max(f.timestamp or 0 for f in flows)
            duration_sec = max(0.1, (max_ts - window_start_ms) / 1000.0)
        else:
            duration_sec = self.window_size_ms / 1000.0
            
        pps = total_packets / duration_sec
        bps = (total_bytes * 8) / duration_sec
        
        src_entropy = self.calculate_entropy(src_ips)
        syn_ratio = total_syn / total_tcp if total_tcp > 0 else 0.0
        
        is_attack = False
        attack_type = None
        evidence = []
        confidence = 0.0
        severity = Severity.HIGH
        
        # Rule 1: SYN Flood (High PPS, High SYN Ratio, High Entropy)
        if pps > self.pps_threshold and syn_ratio > self.syn_ratio_threshold:
            is_attack = True
            if src_entropy > self.spoof_entropy_threshold:
                attack_type = "Spoofed SYN Flood"
                confidence = 0.95
                severity = Severity.CRITICAL
            else:
                attack_type = "Direct SYN Flood"
                confidence = 0.85
                
            evidence.extend([
                EvidenceItem(feature="attack_type", value=attack_type, contribution=0.4),
                EvidenceItem(feature="pps", value=round(pps, 2), contribution=0.3),
                EvidenceItem(feature="syn_ratio", value=round(syn_ratio, 2), contribution=0.2),
                EvidenceItem(feature="source_entropy", value=round(src_entropy, 2), contribution=0.1)
            ])

        # Rule 2: UDP Flood (High PPS/BPS, UDP protocol dominance)
        elif pps > self.pps_threshold and total_udp / total_packets > 0.8:
            is_attack = True
            attack_type = "UDP Flood"
            confidence = 0.90
            if bps > self.bps_threshold:
                severity = Severity.CRITICAL
                
            evidence.extend([
                EvidenceItem(feature="attack_type", value=attack_type, contribution=0.5),
                EvidenceItem(feature="pps", value=round(pps, 2), contribution=0.3),
                EvidenceItem(feature="bps", value=round(bps, 2), contribution=0.2)
            ])
            
        # Benign High-Bandwidth (High BPS, but low SYN ratio and low entropy)
        # -> Will correctly NOT trigger any of the above blocks.

        alerts = []
        if is_attack:
            sample_flow = flows[0]
            obs_score = self.calculate_observability(sample_flow)
            
            alerts.append(Alert(
                alert_id=uuid.uuid4(),
                timestamp=datetime.fromtimestamp(window_start_ms / 1000.0, tz=timezone.utc),
                flow_id="ddos_aggregate",
                source_ip="MULTIPLE" if src_entropy > 1.0 else src_ips[0],
                destination_ip=dst_ip or "UNKNOWN",
                protocol="TCP" if "SYN" in attack_type else "UDP",
                threat_class=ThreatClass.DDoS,
                detector_id=self.detector_id,
                severity=severity,
                confidence=confidence * obs_score,
                observability_score=obs_score,
                evidence=evidence
            ))
            
        return alerts
