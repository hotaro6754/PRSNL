"""Case correlation: group alerts about the same entity and escalate when the
combination tells a stronger story than any single alert."""

from __future__ import annotations

import uuid

from sentinel.alerts import SEVERITIES
from sentinel.store import Store

_VICTIM_CLASSES = {"ddos.syn_flood", "ddos.udp_amplification", "ddos.udp_flood"}
_CASE_GAP_S = 6 * 3600

# (required classes, any-of classes, severity, title)
_RULES = [
    ({"c2.beaconing"}, {"tls.suspicious_session", "tls.known_bad_fingerprint"}, "critical",
     "Encrypted command-and-control channel"),
    ({"dns.dga"}, {"c2.beaconing", "tls.suspicious_session", "tls.known_bad_fingerprint"}, "critical",
     "Malware infection with active C2"),
    ({"dns.tunnel"}, {"exfil.volume", "c2.beaconing"}, "critical", "Covert channel with data leaving the network"),
    ({"recon.scan"}, {"exfil.volume", "c2.beaconing", "dns.tunnel"}, "critical",
     "Reconnaissance followed by C2 or exfiltration"),
    ({"exfil.volume"}, {"tls.suspicious_session", "dns.dga"}, "critical", "Exfiltration from a likely compromised host"),
]


def case_entity(alert: dict) -> str:
    return alert["dst"] if alert["threat_class"] in _VICTIM_CLASSES else alert["src"]


class CaseCorrelator:
    def __init__(self, store: Store) -> None:
        self.store = store

    def ingest(self, alert: dict) -> dict:
        entity = case_entity(alert)
        case = self.store.open_case_for(entity)
        ts = alert["event_time"]
        if case is None or ts - case["last_seen"] > _CASE_GAP_S:
            case = {"case_id": "CASE-" + uuid.uuid4().hex[:10].upper(), "entity": entity, "status": "open",
                    "first_seen": ts, "last_seen": ts, "classes": {}, "alert_count": 0,
                    "severity": alert["severity"], "title": alert["title"]}
        classes = dict(case["classes"])
        classes[alert["threat_class"]] = classes.get(alert["threat_class"], 0) + 1
        present = set(classes)
        severity = max((case["severity"], alert["severity"]), key=SEVERITIES.index)
        title = case["title"] if case["alert_count"] else alert["title"]
        for required, any_of, rule_severity, rule_title in _RULES:
            if required <= present and present & any_of:
                severity = max((severity, rule_severity), key=SEVERITIES.index)
                title = rule_title
                break
        case.update(classes=classes, severity=severity, title=title, alert_count=case["alert_count"] + 1,
                    first_seen=min(case["first_seen"], ts), last_seen=max(case["last_seen"], ts))
        return self.store.upsert_case(case, alert["alert_id"])
