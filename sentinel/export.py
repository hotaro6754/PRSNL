"""Alert export in formats a SOC / national CERT ingests.

* STIX 2.1 bundle  — for MISP, OpenCTI, threat-intel platforms and TAXII feeds.
* CEF (ArcSight)   — one syslog line per alert for a SIEM.

A data diode still needs to move intelligence *out* of the enclave. These
formats are the standard way to do that, and the custody chain hash travels with
each record so the recipient can tie it back to the signed evidence.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

_STIX_ATTACK_PATTERN = {
    "ddos.syn_flood": ("T1498.001", "Network Denial of Service: Direct Network Flood"),
    "ddos.udp_amplification": ("T1498.002", "Network Denial of Service: Reflection Amplification"),
    "ddos.udp_flood": ("T1498.001", "Network Denial of Service: Direct Network Flood"),
    "ddos.slow_http": ("T1499.003", "Endpoint Denial of Service: Application Exhaustion Flood"),
    "c2.beaconing": ("T1071", "Application Layer Protocol"),
    "dns.dga": ("T1568.002", "Dynamic Resolution: Domain Generation Algorithms"),
    "dns.tunnel": ("T1071.004", "Application Layer Protocol: DNS"),
    "tls.known_bad_fingerprint": ("T1573", "Encrypted Channel"),
    "tls.suspicious_session": ("T1573.002", "Encrypted Channel: Asymmetric Cryptography"),
    "recon.scan": ("T1046", "Network Service Discovery"),
    "exfil.volume": ("T1048", "Exfiltration Over Alternative Protocol"),
    "anomaly.behavioural": ("T0000", "Unspecified behavioural anomaly"),
}
_SEVERITY_NUM = {"low": 3, "medium": 5, "high": 7, "critical": 9}


def _ts(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _det_id(namespace: str, value: str) -> str:
    return f"{namespace}--{uuid.uuid5(uuid.NAMESPACE_URL, value)}"


def alert_to_stix_objects(alert: dict, sensor_id: str) -> list[dict]:
    """Return the STIX SDOs/SCOs for one alert (indicator + observed-data + sighting)."""
    aid = alert["alert_id"]
    created = _ts(alert["event_time"])
    tech, name = _STIX_ATTACK_PATTERN.get(alert["threat_class"], ("T0000", alert["threat_class"]))
    src = alert.get("src", "")
    dst = alert.get("dst", "")
    evidence = "; ".join(f"{e['feature']}={e['value']}" for e in alert.get("evidence", [])[:8])
    pattern_bits = []
    if _is_ip(src):
        pattern_bits.append(f"ipv4-addr:value = '{src}'")
    if _is_ip(dst):
        pattern_bits.append(f"ipv4-addr:value = '{dst}'")
    domain = dst if (dst and not _is_ip(dst) and "." in dst) else None
    if domain:
        pattern_bits.append(f"domain-name:value = '{domain}'")
    pattern = "[" + " OR ".join(pattern_bits) + "]" if pattern_bits else "[network-traffic:protocols[*] = 'ip']"

    indicator = {
        "type": "indicator", "spec_version": "2.1", "id": _det_id("indicator", aid),
        "created": created, "modified": created, "name": f"{name} ({alert['threat_class']})",
        "description": f"{alert.get('title', '')}. Evidence: {evidence}",
        "indicator_types": ["malicious-activity"], "pattern": pattern, "pattern_type": "stix",
        "valid_from": created, "confidence": int(round(alert.get("confidence", 0) * 100)),
        "labels": [alert["severity"], alert["threat_class"]],
        "external_references": [
            {"source_name": "mitre-attack", "external_id": tech},
            {"source_name": "sentinel-26145", "external_id": aid,
             "description": f"custody chain hash {(alert.get('custody') or {}).get('hash', 'n/a')}"},
        ],
    }
    identity = {
        "type": "identity", "spec_version": "2.1", "id": _det_id("identity", sensor_id),
        "created": created, "modified": created, "name": sensor_id, "identity_class": "system",
        "description": "Sentinel-26145 passive one-way traffic sensor",
    }
    sighting = {
        "type": "sighting", "spec_version": "2.1", "id": _det_id("sighting", aid),
        "created": created, "modified": created, "sighting_of_ref": indicator["id"],
        "where_sighted_refs": [identity["id"]], "count": 1,
        "first_seen": _ts(alert["window_start"]), "last_seen": _ts(alert["window_end"]),
    }
    return [identity, indicator, sighting]


def alerts_to_stix_bundle(alerts: list[dict], sensor_id: str) -> dict:
    objects: list[dict] = []
    seen_ids: set[str] = set()
    for alert in alerts:
        for obj in alert_to_stix_objects(alert, sensor_id):
            if obj["id"] not in seen_ids or obj["type"] != "identity":
                seen_ids.add(obj["id"])
                objects.append(obj)
    return {"type": "bundle", "id": f"bundle--{uuid.uuid4()}", "objects": objects}


def alert_to_cef(alert: dict, sensor_id: str) -> str:
    """ArcSight Common Event Format line."""
    tech, name = _STIX_ATTACK_PATTERN.get(alert["threat_class"], ("T0000", alert["threat_class"]))
    header = f"CEF:0|NTRO|Sentinel-26145|1.0|{alert['threat_class']}|{name}|{_SEVERITY_NUM.get(alert['severity'], 5)}|"
    ext = {
        "rt": int(alert["event_time"] * 1000),
        "src": alert.get("src", ""),
        "dst": alert.get("dst", ""),
        "dpt": alert.get("dport") or "",
        "cs1Label": "threatClass", "cs1": alert["threat_class"],
        "cs2Label": "mitreTechnique", "cs2": tech,
        "cs3Label": "custodyHash", "cs3": (alert.get("custody") or {}).get("hash", ""),
        "cn1Label": "confidencePct", "cn1": int(round(alert.get("confidence", 0) * 100)),
        "cat": alert.get("category", ""),
        "deviceExternalId": sensor_id,
        "msg": _cef_escape(alert.get("title", "")),
        "externalId": alert["alert_id"],
    }
    body = " ".join(f"{k}={_cef_escape(str(v))}" for k, v in ext.items() if v != "")
    return header + body


def _cef_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("=", "\\=").replace("\n", " ").replace("|", "\\|")


def _is_ip(value: str) -> bool:
    import ipaddress
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def export_alerts(alerts: list[dict], fmt: str, sensor_id: str) -> tuple[str, str]:
    """Return (body, content_type) for the requested format."""
    if fmt == "stix":
        return json.dumps(alerts_to_stix_bundle(alerts, sensor_id), indent=2), "application/stix+json"
    if fmt == "cef":
        return "\n".join(alert_to_cef(a, sensor_id) for a in alerts) + "\n", "text/plain"
    if fmt == "jsonl":
        return "\n".join(json.dumps(a, separators=(",", ":")) for a in alerts) + "\n", "application/x-ndjson"
    raise ValueError(f"unknown export format {fmt!r}")
