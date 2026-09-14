"""Evaluate the full pipeline on a labelled capture.

Runs the capture through the same Engine the service uses, then matches alerts
to ground truth:

* an attack is DETECTED if an alert of the same class names one of its entities
  (src or dst) and its event time falls inside [t0 - 5 s, t1 + 300 s]
* every alert that matches no attack is a FALSE ALERT
* detection delay = first matching alert's event time - attack start (event time)

Writes a JSON report and prints a table.

    python ml/evaluate.py lab/captures/lab.pcap --report results/eval.json
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentinel import __version__  # noqa: E402
from sentinel.config import Settings  # noqa: E402
from sentinel.custody import SensorKey  # noqa: E402
from sentinel.engine import Engine  # noqa: E402
from sentinel.store import Store  # noqa: E402

# An attack labelled with one class may legitimately raise a closely related class.
EQUIVALENT = {"c2.beaconing": {"c2.beaconing"}, "tls.suspicious_session": {"tls.suspicious_session", "tls.known_bad_fingerprint"}}


def matches(alert: dict, attack: dict) -> bool:
    classes = EQUIVALENT.get(attack["threat_class"], {attack["threat_class"]})
    if alert["threat_class"] not in classes:
        return False
    entities = {e for e in (attack.get("src"), attack.get("dst")) if e}
    if not entities & {alert["src"], alert["dst"]}:
        return False
    return attack["t0"] - 5 <= alert["event_time"] <= attack["t1"] + 300


def evaluate(capture: str, truth_path: str, data_dir: str) -> dict:
    truth = json.loads(Path(truth_path).read_text(encoding="utf-8"))
    settings = Settings(internal_nets=tuple(truth.get("internal_nets", Settings().internal_nets)), data_dir=data_dir)
    settings.exfil.allow_destinations = tuple(truth.get("allow_destinations", ()))
    store = Store(str(Path(data_dir) / "eval.db"), SensorKey.load_or_create(data_dir))
    engine = Engine(settings, store)
    wall = time.time()
    summary = engine.run_capture(capture, label="evaluation")
    alerts = store.list_alerts(limit=100_000)
    chain = store.verify_chain()

    attacks = truth["attacks"]
    per_class: dict = defaultdict(lambda: {"attacks": 0, "detected": 0, "alerts": 0, "false_alerts": 0, "delays_s": []})
    matched_alerts = set()
    for attack in attacks:
        cls = attack["threat_class"]
        row = per_class[cls]
        row["attacks"] += 1
        hits = sorted((a for a in alerts if matches(a, attack)), key=lambda a: a["event_time"])
        if hits:
            row["detected"] += 1
            row["delays_s"].append(round(hits[0]["event_time"] - attack["t0"], 2))
            matched_alerts.update(a["alert_id"] for a in hits)
    # The unsupervised anomaly net (category "-") is a supporting signal, not one of the
    # six labelled PS classes; its unmatched alerts are reported separately, not counted
    # as false positives against the named detectors.
    false_alerts = []
    anomaly_alerts = []
    for alert in alerts:
        if alert.get("category") == "-":
            anomaly_alerts.append(alert)
            continue
        row = per_class[alert["threat_class"]]
        row["alerts"] += 1
        if alert["alert_id"] not in matched_alerts:
            row["false_alerts"] += 1
            false_alerts.append({k: alert[k] for k in ("threat_class", "src", "dst", "confidence", "title", "event_time")})

    hours = truth["duration_hours"]
    classes = {}
    for cls, row in sorted(per_class.items()):
        classes[cls] = {
            "attacks": row["attacks"], "detected": row["detected"],
            "recall": round(row["detected"] / row["attacks"], 3) if row["attacks"] else None,
            "alerts": row["alerts"], "false_alerts": row["false_alerts"],
            "precision": round((row["alerts"] - row["false_alerts"]) / row["alerts"], 3) if row["alerts"] else None,
            "false_alerts_per_hour": round(row["false_alerts"] / hours, 3),
            "detection_delay_s": row["delays_s"],
        }
    total_attacks = len(attacks)
    detected = sum(r["detected"] for r in per_class.values())
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(wall)),
        "sentinel_version": __version__,
        "capture": Path(capture).name,
        "capture_sha256": summary["capture_sha256"],
        "synthetic": truth.get("synthetic", False),
        "duration_hours": hours,
        "host": {"platform": platform.platform(), "processor": platform.processor(), "python": platform.python_version()},
        "overall": {
            "attacks": total_attacks, "detected": detected,
            "recall": round(detected / total_attacks, 3) if total_attacks else None,
            "alerts": len(alerts), "false_alerts": len(false_alerts),
            "false_alerts_per_hour": round(len(false_alerts) / hours, 3),
        },
        "per_class": classes,
        "anomaly_supporting": {
            "alerts": len(anomaly_alerts),
            "per_hour": round(len(anomaly_alerts) / hours, 3),
            "note": "unsupervised behavioural anomaly net; supporting signal only, not one of the six PS classes",
            "hosts": sorted({a["src"] for a in anomaly_alerts})[:20],
        },
        "false_alert_samples": false_alerts[:25],
        "pipeline": {k: summary[k] for k in ("packets", "flows", "elapsed_s", "packets_per_s", "flows_per_s", "mbit_per_s",
                                             "alert_latency_ms_p50", "alert_latency_ms_p99", "event_latency_ms_p50",
                                             "event_latency_ms_p99", "detector_errors")},
        "custody_chain": chain,
        "dga_model": engine.dga_model.ref().model_dump() if engine.dga_model else None,
    }
    store.close()
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("capture")
    ap.add_argument("--truth", default=None)
    ap.add_argument("--report", default="results/evaluation.json")
    args = ap.parse_args()
    truth = args.truth or str(Path(args.capture).with_suffix(".truth.json"))
    with tempfile.TemporaryDirectory() as tmp:
        report = evaluate(args.capture, truth, tmp)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    o = report["overall"]
    print(f"{report['capture']} ({report['duration_hours']} h, synthetic={report['synthetic']})")
    print(f"{'class':<28}{'attacks':>8}{'found':>7}{'alerts':>8}{'false':>7}{'false/h':>9}  delay_s")
    for cls, row in report["per_class"].items():
        print(f"{cls:<28}{row['attacks']:>8}{row['detected']:>7}{row['alerts']:>8}{row['false_alerts']:>7}"
              f"{row['false_alerts_per_hour']:>9}  {row['detection_delay_s']}")
    print(f"overall recall={o['recall']} alerts={o['alerts']} false={o['false_alerts']} ({o['false_alerts_per_hour']}/h)")
    a = report["anomaly_supporting"]
    print(f"anomaly (supporting, not scored against PS classes): {a['alerts']} alerts ({a['per_hour']}/h)")
    p = report["pipeline"]
    print(f"pipeline: {p['packets']} packets, {p['flows']} flows in {p['elapsed_s']} s -> {p['packets_per_s']} pkt/s, "
          f"{p['flows_per_s']} flows/s; event latency p99 {p['event_latency_ms_p99']} ms")
    print(f"custody chain: {report['custody_chain']['ok']} ({report['custody_chain']['checked']} records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
