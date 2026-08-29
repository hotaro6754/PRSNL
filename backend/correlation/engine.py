import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging

from backend.schemas import Alert, CyberCase
from backend.config import ThreatClass, Severity

logger = logging.getLogger(__name__)

class CorrelationEngine:
    def __init__(self, max_cases: int = 1000, max_alerts_per_case: int = 50, case_ttl_seconds: int = 86400):
        self.cases: Dict[str, CyberCase] = {} # Keyed by primary_entity
        self.max_cases = max_cases
        self.max_alerts_per_case = max_alerts_per_case
        self.case_ttl_seconds = case_ttl_seconds

    def ingest_alert(self, alert: Alert) -> Optional[CyberCase]:
        """
        Ingests a raw alert and correlates it into a CyberCase.
        Returns the updated CyberCase.
        """
        entity = alert.primary_entity or alert.source_ip
        if not entity or entity == "UNKNOWN":
            return None

        # 1. Deduplication and Garbage Collection
        self._garbage_collect(current_time=alert.timestamp)
        
        # Enforce global case memory bound
        if entity not in self.cases and len(self.cases) >= self.max_cases:
            logger.warning("Correlation Engine hit MAX_CASES boundary. Dropping new case.")
            return None

        if entity not in self.cases:
            # Create new case
            case = CyberCase(
                case_id=uuid.uuid4(),
                primary_entity=entity,
                source_ip=alert.source_ip,
                status="OPEN",
                severity=alert.severity,
                threat_summary=f"Isolated {alert.threat_class} detected",
                first_seen=alert.timestamp,
                last_seen=alert.timestamp,
                alerts=[alert]
            )
            self.cases[entity] = case
        else:
            # Update existing case
            case = self.cases[entity]
            case.last_seen = alert.timestamp
            
            # Deduplication: don't store exact duplicate alerts based on threat class + destination + time window if they are extremely close.
            # For memory safety, we just cap at max_alerts_per_case, acting as a sliding window of evidence.
            if len(case.alerts) >= self.max_alerts_per_case:
                case.alerts.pop(0) # Evict oldest evidence to prevent memory unboundedness
            
            case.alerts.append(alert)
            if alert.evidence and case.evidence is not None:
                case.evidence.extend(alert.evidence)
            elif alert.evidence:
                case.evidence = list(alert.evidence)
            
        # 2. Relationship Correlation (Severity & Summary Escalation)
        self._evaluate_case_escalation(case)
            
        return case

    def _evaluate_case_escalation(self, case: CyberCase):
        """
        Analyzes the set of alerts inside a case and escalates the severity / summary
        based on behavioral patterns, strictly avoiding blind confidence summation.
        """
        threat_counts = {}
        destinations = set()
        
        for alert in case.alerts:
            threat_counts[alert.threat_class] = threat_counts.get(alert.threat_class, 0) + 1
            if alert.destination_ip and alert.destination_ip != "UNKNOWN":
                destinations.add(alert.destination_ip)
                
        has_dga = threat_counts.get(ThreatClass.DGA, 0) > 0
        has_tls = threat_counts.get(ThreatClass.TLSAnomaly, 0) > 0
        has_beacon = threat_counts.get(ThreatClass.Beaconing, 0) > 0
        has_tunnel = threat_counts.get(ThreatClass.Tunneling, 0) > 0
        has_scan = threat_counts.get(ThreatClass.PortScan, 0) > 0
        has_outbound = len(destinations) > 0
        
        # Rule 1: DGA + TLS Anomaly -> SUSPICIOUS_ENCRYPTED_C2_BEHAVIOR
        if has_dga and has_tls:
            case.severity = "CRITICAL"
            case.threat_summary = "Suspected Encrypted C2 Behavior (DGA + TLS Fingerprint)"
            
        # Rule 2: Beaconing + TLS Anomaly -> SUSPICIOUS_ENCRYPTED_BEHAVIOR
        elif has_beacon and has_tls:
            case.severity = "CRITICAL"
            case.threat_summary = "Suspected Encrypted C2 Behavior (Beaconing + TLS Fingerprint)"
            
        # Rule 3: DNS Tunnel + Outbound Data
        elif has_tunnel:
            case.severity = "CRITICAL"
            case.threat_summary = "Possible Data Channel / Exfiltration (DNS Tunnelling)"
            
        # Rule 4: Port Scan + Subsequent Outbound Connections
        elif has_scan and has_outbound and sum(threat_counts.values()) > threat_counts.get(ThreatClass.PortScan, 0):
            case.severity = "HIGH"
            case.threat_summary = "Reconnaissance Chain (Scan followed by connections)"
            
        # Default single-threat fallbacks (Deduplication prevents infinite escalation)
        else:
            if has_dga or has_beacon:
                case.severity = "MEDIUM" # Even 100 DGA alerts alone only mean MEDIUM.
                case.threat_summary = f"Persistent {list(threat_counts.keys())[0]} behavior"
            elif has_scan:
                case.severity = "MEDIUM"
                case.threat_summary = "Isolated Reconnaissance Scanning"

    def _garbage_collect(self, current_time: datetime):
        """Purge cases that have exceeded their TTL."""
        expired = []
        for entity, case in self.cases.items():
            delta = (current_time - case.last_seen).total_seconds()
            if delta > self.case_ttl_seconds:
                expired.append(entity)
                
        for entity in expired:
            del self.cases[entity]

    def get_all_cases(self) -> List[CyberCase]:
        return list(self.cases.values())
