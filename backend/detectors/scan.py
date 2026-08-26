from backend.contracts.observation import NetworkObservation
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.config import ThreatClass, Severity
from collections import defaultdict

class PortScanDetector(BaseDetector):
    def __init__(self, window_size_ms: int = 10000):
        super().__init__(window_size_ms=window_size_ms, detector_id="scan_v2")
        self.vertical_scan_threshold = 20   # Unique ports per dst_ip
        self.horizontal_scan_threshold = 20 # Unique dst_ips per port

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        if not flows:
            return []

        # Tracking for Vertical Scans (One IP scanning many ports on a single target)
        src_to_dst_ports = defaultdict(lambda: defaultdict(set))
        # Tracking for Horizontal Scans (One IP scanning a single port across many targets)
        src_to_port_dsts = defaultdict(lambda: defaultdict(set))

        for flow in flows:
            src = flow.source_ip
            dst = flow.destination_ip
            port = flow.destination_port
            
            if src and dst and port is not None:
                src_to_dst_ports[src][dst].add(port)
                src_to_port_dsts[src][port].add(dst)

        alerts = []
        alerted_srcs = set() # Avoid emitting both horizontal and vertical for same src in same window

        # Evaluate Vertical Scans
        for src, dsts in src_to_dst_ports.items():
            for dst, ports in dsts.items():
                if len(ports) > self.vertical_scan_threshold:
                    sample_flow = next((f for f in flows if f.source_ip == src), None)
                    obs_score = self.calculate_observability(sample_flow) if sample_flow else 0.5
                    
                    alerts.append(Alert(
                        alert_id=uuid.uuid4(),
                        timestamp=datetime.fromtimestamp(window_start_ms / 1000.0, tz=timezone.utc),
                        flow_id="scan_vertical",
                        source_ip=src,
                        destination_ip=dst,
                        protocol="MULTIPLE",
                        threat_class=ThreatClass.PortScan,
                        detector_id=self.detector_id,
                        severity=Severity.HIGH,
                        confidence=0.90 * obs_score,
                        observability_score=obs_score,
                        evidence=[
                            EvidenceItem(feature="scan_type", value="vertical", contribution=0.0),
                            EvidenceItem(feature="unique_destination_ports", value=len(ports), contribution=0.9),
                            EvidenceItem(feature="time_window_ms", value=self.window_size_ms, contribution=0.1)
                        ]
                    ))
                    alerted_srcs.add(src)

        # Evaluate Horizontal Scans
        for src, ports in src_to_port_dsts.items():
            if src in alerted_srcs:
                continue
            for port, dsts in ports.items():
                if len(dsts) > self.horizontal_scan_threshold:
                    # Behavioral heuristic: A bare SYN scanner sends exactly 1 packet per destination.
                    # Benign web browsing sends multiple outgoing packets (SYN, ACK, Data) per destination.
                    flows_for_this_scan = [f for f in flows if f.source_ip == src and f.destination_port == port]
                    total_packets = sum(f.orig_packets for f in flows_for_this_scan)
                    avg_packets_per_dst = total_packets / len(dsts)
                    
                    if avg_packets_per_dst > 1.5:
                        continue # High-fanout benign traffic (multiple packets per IP), not a bare SYN scan.
                    sample_flow = next((f for f in flows if f.source_ip == src), None)
                    obs_score = self.calculate_observability(sample_flow) if sample_flow else 0.5
                    
                    alerts.append(Alert(
                        alert_id=uuid.uuid4(),
                        timestamp=datetime.fromtimestamp(window_start_ms / 1000.0, tz=timezone.utc),
                        flow_id="scan_horizontal",
                        source_ip=src,
                        destination_ip="MULTIPLE",
                        protocol=str(port),
                        threat_class=ThreatClass.PortScan,
                        detector_id=self.detector_id,
                        severity=Severity.HIGH,
                        confidence=0.90 * obs_score,
                        observability_score=obs_score,
                        evidence=[
                            EvidenceItem(feature="scan_type", value="horizontal", contribution=0.0),
                            EvidenceItem(feature="targeted_port", value=port, contribution=0.0),
                            EvidenceItem(feature="unique_destination_ips", value=len(dsts), contribution=0.9),
                            EvidenceItem(feature="time_window_ms", value=self.window_size_ms, contribution=0.1)
                        ]
                    ))
                    alerted_srcs.add(src)

        return alerts
