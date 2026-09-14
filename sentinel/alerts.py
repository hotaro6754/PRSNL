"""Alert record schema (PS 26145 constraint e).

Every alert is a structured, versioned record: timestamp, flow identifiers,
threat class, calibrated/declared confidence, supporting evidence, the
visibility the evidence was gathered under, the detector/model that produced it
and its place in the tamper-evident custody chain.

Alerts are intelligence only. ``advisory`` lists steps for a human operating
outside the monitoring enclave; nothing here is ever sent back across the tap.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "sentinel.alert/1.0"


class ThreatClass(StrEnum):
    SYN_FLOOD = "ddos.syn_flood"
    UDP_AMPLIFICATION = "ddos.udp_amplification"
    UDP_FLOOD = "ddos.udp_flood"
    BEACONING = "c2.beaconing"
    DGA = "dns.dga"
    DNS_TUNNEL = "dns.tunnel"
    TLS_KNOWN_BAD = "tls.known_bad_fingerprint"
    TLS_SUSPICIOUS = "tls.suspicious_session"
    SLOW_HTTP = "ddos.slow_http"
    SCAN = "recon.scan"
    EXFILTRATION = "exfil.volume"
    ANOMALY = "anomaly.behavioural"


# Problem-statement category (a-f) and MITRE ATT&CK technique for each class.
CLASS_META: dict[ThreatClass, tuple[str, str, str]] = {
    ThreatClass.SYN_FLOOD: ("a", "T1498.001", "TCP SYN flood"),
    ThreatClass.UDP_AMPLIFICATION: ("a", "T1498.002", "UDP reflection / amplification"),
    ThreatClass.UDP_FLOOD: ("a", "T1498.001", "UDP flood"),
    ThreatClass.SLOW_HTTP: ("a", "T1499.003", "Slow-HTTP resource exhaustion"),
    ThreatClass.BEACONING: ("b", "T1071", "Periodic C2 beaconing"),
    ThreatClass.DGA: ("c", "T1568.002", "DGA domain lookups"),
    ThreatClass.DNS_TUNNEL: ("c", "T1071.004", "DNS tunnelling"),
    ThreatClass.TLS_KNOWN_BAD: ("d", "T1573", "Known-bad TLS client fingerprint"),
    ThreatClass.TLS_SUSPICIOUS: ("d", "T1573.002", "Suspicious encrypted session"),
    ThreatClass.SCAN: ("e", "T1046", "Reconnaissance / scanning"),
    ThreatClass.EXFILTRATION: ("f", "T1048", "Asymmetric outbound data volume"),
    ThreatClass.ANOMALY: ("-", "T0000", "Unsupervised behavioural anomaly"),
}

SEVERITIES = ("low", "medium", "high", "critical")


class Evidence(BaseModel):
    feature: str
    value: Any
    baseline: Any = None
    threshold: Any = None
    unit: str | None = None
    note: str | None = None


class Visibility(BaseModel):
    """What the sensor actually saw while forming this alert."""

    directions_seen: float = Field(description="mean directions observed per contributing flow (1 or 2)")
    handshake_seen: bool | None = None
    est_loss_pct: float = 0.0
    sufficient: bool = True
    note: str | None = None


class ModelRef(BaseModel):
    name: str
    version: str
    sha256: str
    calibration: str | None = None


class PacketPointer(BaseModel):
    index: int
    offset: int


class EvidenceScope(BaseModel):
    """How to cut the supporting packets back out of the source capture."""

    hosts: list[str] = Field(default_factory=list)
    ports: list[int] = Field(default_factory=list)
    proto: int | None = None
    t0: float
    t1: float
    offset_lo: int = -1
    offset_hi: int = -1
    max_packets: int = 5000


class Custody(BaseModel):
    source_id: str
    source_sha256: str | None = None
    packets: list[PacketPointer] = Field(default_factory=list)
    scope: EvidenceScope | None = None
    seq: int | None = None
    prev_hash: str | None = None
    hash: str | None = None
    signature: str | None = None


class Alert(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: str = Field(default=SCHEMA_VERSION, alias="schema")
    alert_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    sensor_id: str = "sentinel-01"
    emitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_time: float = Field(description="epoch seconds of the last observation that triggered the alert")
    window_start: float
    window_end: float
    processing_latency_ms: float = 0.0
    threat_class: ThreatClass
    category: str
    attack_technique: str
    title: str
    severity: str
    confidence: float = Field(ge=0.0, le=1.0)
    src: str
    dst: str
    dport: int | None = None
    flow_ids: list[str] = Field(default_factory=list, description="Community ID v1 of contributing flows")
    evidence: list[Evidence]
    visibility: Visibility
    detector: str
    model: ModelRef | None = None
    custody: Custody | None = None
    advisory: list[str] = Field(default_factory=list)

    def public_dict(self) -> dict:
        return json.loads(self.model_dump_json(by_alias=True))


def make_alert(threat_class: ThreatClass, **fields) -> Alert:
    category, technique, title = CLASS_META[threat_class]
    fields.setdefault("title", title)
    return Alert(threat_class=threat_class, category=category, attack_technique=technique, **fields)


def severity_for(confidence: float, impact: str = "medium") -> str:
    """Severity combines how sure we are with how bad the class is if true."""
    rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}[impact]
    if confidence < 0.5:
        rank -= 2
    elif confidence < 0.75:
        rank -= 1
    return SEVERITIES[max(0, min(3, rank))]


def json_schema() -> dict:
    return Alert.model_json_schema(by_alias=True)
