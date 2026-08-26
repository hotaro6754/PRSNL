"""
SlowHTTPDetector — Passive detection of slow HTTP resource exhaustion (Slowloris-style).

Root cause analysis:
  Slowloris opens many concurrent TCP connections to a single HTTP(S) port
  and sends incomplete requests at a very slow rate, holding connections open
  and exhausting server resources. The behavioral signature is:

  1. Many TCP connections from ONE source to ONE destination port (80/443/8080/8443)
  2. Abnormally LOW bytes per connection
  3. Long connection durations (or incomplete state — no FIN from originator)
  4. Very low packet rate per connection

  This is NOT reconnaissance (no port fan-out).
  This is NOT volumetric DDoS (low total bytes/packets).
  This IS application-layer resource exhaustion visible from passive metadata.

Detection approach:
  Within each tumbling window, count TCP flows to HTTP ports from the same source.
  If the window contains many concurrent low-throughput, incomplete connections
  concentrated on a single destination port, flag as SlowHTTP exhaustion.

  All features are derived from NetworkObservation metadata.
  No payload inspection. No active probing. Bounded window state.
"""

from backend.contracts.observation import NetworkObservation
from typing import List
import uuid
from datetime import datetime, timezone
from collections import defaultdict
from backend.detectors.base import BaseDetector
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.config import ThreatClass, Severity


# HTTP-family ports
HTTP_PORTS = {80, 443, 8080, 8443, 8000, 8888}


class SlowHTTPDetector(BaseDetector):
    """
    Detects Slowloris / slow HTTP exhaustion using passive connection metadata.

    Thresholds:
      min_connections:        minimum concurrent TCP flows to trigger analysis (10)
      max_bytes_per_conn:     connections averaging above this are normal (500 bytes)
      min_incomplete_ratio:   fraction of connections missing FIN from originator (0.5)
      min_port_concentration: fraction of flows targeting the same dst port (0.7)
    """

    def __init__(self, window_size_ms: int = 10000):
        super().__init__(window_size_ms=window_size_ms, detector_id="slow_http_v1")
        self.min_connections = 10
        self.max_bytes_per_conn = 500  # bytes — Slowloris sends tiny trickles
        self.min_incomplete_ratio = 0.5
        self.min_port_concentration = 0.7

    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        if not flows:
            return []

        # Only consider TCP flows to HTTP ports
        http_flows = [
            f for f in flows
            if f.protocol == 6 and f.destination_port in HTTP_PORTS
        ]

        if len(http_flows) < self.min_connections:
            return []

        # --- Feature extraction (all passive, bounded) ---

        # 1. Connection count
        conn_count = len(http_flows)

        # 2. Bytes per connection (originator bytes)
        total_orig_bytes = sum(f.orig_ip_bytes for f in http_flows)
        avg_bytes_per_conn = total_orig_bytes / max(conn_count, 1)

        # 3. Incomplete connection ratio (no FIN from originator = held open)
        incomplete = sum(1 for f in http_flows if not f.tcp_fin_orig)
        incomplete_ratio = incomplete / max(conn_count, 1)

        # 4. Destination port concentration
        port_counts: dict = defaultdict(int)
        for f in http_flows:
            port_counts[f.destination_port] += 1
        max_port_count = max(port_counts.values()) if port_counts else 0
        port_concentration = max_port_count / max(conn_count, 1)

        # 5. Destination IP concentration (Slowloris targets one server)
        dst_counts: dict = defaultdict(int)
        for f in http_flows:
            dst_counts[f.destination_ip] += 1
        max_dst_count = max(dst_counts.values()) if dst_counts else 0
        dst_concentration = max_dst_count / max(conn_count, 1)

        # 6. Average packets per connection (Slowloris = very few)
        total_packets = sum(f.orig_packets for f in http_flows)
        avg_pkts_per_conn = total_packets / max(conn_count, 1)

        # --- Decision ---
        is_slow_http = (
            avg_bytes_per_conn <= self.max_bytes_per_conn
            and incomplete_ratio >= self.min_incomplete_ratio
            and port_concentration >= self.min_port_concentration
        )

        if not is_slow_http:
            return []

        # Confidence scales with how many signals align
        confidence = 0.0
        confidence += 0.30 if conn_count >= 20 else 0.15
        confidence += 0.25 if avg_bytes_per_conn < 200 else 0.10
        confidence += 0.25 if incomplete_ratio > 0.8 else 0.10
        confidence += 0.20 if dst_concentration > 0.8 else 0.05

        # Determine the primary target
        primary_dst = max(dst_counts, key=dst_counts.get)
        primary_port = max(port_counts, key=port_counts.get)

        sample_flow = http_flows[0]
        obs_score = self.calculate_observability(sample_flow)

        alert = Alert(
            alert_id=uuid.uuid4(),
            timestamp=datetime.fromtimestamp(
                (window_start_ms or 0) / 1000.0, tz=timezone.utc
            ),
            flow_id=f"slow_http_{sample_flow.source_ip}_{primary_port}",
            source_ip=sample_flow.source_ip,
            destination_ip=primary_dst,
            protocol="TCP",
            threat_class=ThreatClass.SlowHTTP,  # Application-layer resource exhaustion
            detector_id=self.detector_id,
            severity=Severity.HIGH,
            confidence=round(min(confidence, 1.0) * obs_score, 4),
            observability_score=obs_score,
            evidence=[
                EvidenceItem(
                    feature="concurrent_http_connections",
                    value=conn_count,
                    contribution=0.25,
                    explanation="Number of concurrent TCP connections to HTTP ports in this window",
                ),
                EvidenceItem(
                    feature="avg_bytes_per_connection",
                    value=round(avg_bytes_per_conn, 2),
                    contribution=0.25,
                    explanation="Abnormally low originator bytes per connection indicates trickle sending",
                ),
                EvidenceItem(
                    feature="incomplete_connection_ratio",
                    value=round(incomplete_ratio, 4),
                    contribution=0.25,
                    explanation="Fraction of connections without FIN from originator (held open)",
                ),
                EvidenceItem(
                    feature="destination_port_concentration",
                    value=round(port_concentration, 4),
                    contribution=0.15,
                    explanation="Fraction of connections targeting the same destination port",
                ),
                EvidenceItem(
                    feature="avg_packets_per_connection",
                    value=round(avg_pkts_per_conn, 2),
                    contribution=0.10,
                    explanation="Very low packets per connection is characteristic of slow HTTP attacks",
                ),
            ],
        )

        return [alert]
