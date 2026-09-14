"""Deterministic, offline explanation of an alert.

Turns the alert's own evidence into a short analyst-readable paragraph. It is a
template over recorded facts — no model, no network — so the explanation is
reproducible and cannot hallucinate. The dashboard shows it; the CLI can print it.
"""

from __future__ import annotations

from sentinel.alerts import CLASS_META

_CATEGORY = {
    "a": "volumetric / protocol denial of service",
    "b": "botnet command-and-control beaconing",
    "c": "DGA domains or DNS tunnelling",
    "d": "malware inside an encrypted session",
    "e": "reconnaissance or scanning",
    "f": "data exfiltration",
    "-": "an unnamed behavioural anomaly",
}


def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, list):
        return ", ".join(str(x) for x in value[:6])
    return str(value)


def explain(alert: dict) -> dict:
    cls = alert["threat_class"]
    category = alert.get("category", "-")
    technique = alert.get("attack_technique", "")
    src, dst = alert.get("src", "?"), alert.get("dst", "?")
    conf = alert.get("confidence", 0)
    sev = alert.get("severity", "unknown")

    lead = (f"Sentinel classified traffic from {src} to {dst} as "
            f"{alert.get('title', cls)} - {_CATEGORY.get(category, cls)} "
            f"(MITRE ATT&CK {technique}). Severity {sev}, confidence {conf:.0%}.")

    # the strongest evidence lines: those with a threshold the value crossed
    reasons = []
    for ev in alert.get("evidence", []):
        feat, val, thr, base = ev.get("feature"), ev.get("value"), ev.get("threshold"), ev.get("baseline")
        if val is None:
            continue
        unit = f" {ev['unit']}" if ev.get("unit") else ""
        if thr is not None:
            reasons.append(f"{feat.replace('_', ' ')} was {_fmt(val)}{unit} (threshold {_fmt(thr)}{unit})")
        elif base is not None:
            reasons.append(f"{feat.replace('_', ' ')} was {_fmt(val)}{unit} against a baseline of {_fmt(base)}{unit}")
    why = ""
    if reasons:
        why = "It fired because " + "; ".join(reasons[:4]) + "."

    vis = alert.get("visibility", {})
    caveat = ""
    if vis.get("note"):
        caveat = f"Visibility note: {vis['note']}."
    elif vis.get("directions_seen", 2) < 2:
        caveat = "Only one direction of this traffic was visible on the tap; confidence is discounted accordingly."

    model = alert.get("model")
    model_line = ""
    if model:
        model_line = f"The score used model {model['name']} {model['version']} (sha256 {model['sha256'][:12]}...)."

    custody = alert.get("custody", {})
    trace = ""
    if custody.get("hash"):
        trace = (f"The record is chain entry #{custody.get('seq')} "
                 f"(hash {custody['hash'][:12]}...); export its evidence bundle to verify the packets offline.")

    advisory = alert.get("advisory", [])
    return {
        "alert_id": alert.get("alert_id"),
        "summary": lead,
        "why": why,
        "caveat": caveat,
        "model": model_line,
        "custody": trace,
        "next_steps": advisory,
        "text": " ".join(p for p in (lead, why, caveat, model_line, trace) if p),
    }
