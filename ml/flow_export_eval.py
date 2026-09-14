"""Convert a lab capture to a NetFlow v5 export stream and evaluate flow-export mode.

Flow-export mode has no packet payload, so only the flow-observable classes can
fire (DDoS family, scanning, beaconing, exfiltration, slow-HTTP). This measures
detection for exactly those classes, to demonstrate the NetFlow/IPFIX ingest path
the problem statement names.

    python ml/flow_export_eval.py lab/captures/lab-30m.pcap --report results/flow-export-eval.json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentinel.config import Settings  # noqa: E402
from sentinel.custody import SensorKey  # noqa: E402
from sentinel.engine import Engine  # noqa: E402
from sentinel.ingest.flowmeter import FlowMeter  # noqa: E402
from sentinel.ingest.pcapio import PcapReader  # noqa: E402
from sentinel.lab.netflow_export import write_v5  # noqa: E402
from sentinel.store import Store  # noqa: E402

FLOW_CLASSES = {"ddos.syn_flood", "ddos.udp_amplification", "ddos.udp_flood", "ddos.slow_http",
                "recon.scan", "c2.beaconing", "exfil.volume"}
_FLAGS = {"S": 0x02, "A": 0x10, "F": 0x01, "R": 0x04, "P": 0x08}


def pcap_to_flows(capture: str, internal_nets) -> list[dict]:
    """Run the packet flow meter and collect exported flows as NetFlow-style dicts."""
    flows: list[dict] = []

    def sink(ev):
        from sentinel.events import FlowRecord
        if not isinstance(ev, FlowRecord):
            return
        flags = 0
        if ev.syn:
            flags |= _FLAGS["S"]
        if ev.state in ("established", "closed"):
            flags |= _FLAGS["A"]
        if ev.state == "closed":
            flags |= _FLAGS["F"]
        if ev.rst_from_resp or ev.state == "rejected":
            flags |= _FLAGS["R"]
        # originator direction only (a real unidirectional flow export record)
        flows.append({"src": ev.src, "dst": ev.dst, "sport": ev.sport, "dport": ev.dport, "proto": ev.proto,
                      "pkts": max(1, ev.orig_pkts), "octets": max(40, ev.orig_bytes),
                      "first": ev.first_ts, "last": ev.last_ts, "flags": flags})
        if ev.resp_pkts:  # the reverse direction is a separate export record
            rflags = _FLAGS["A"] | (_FLAGS["S"] if ev.synack else 0)
            flows.append({"src": ev.dst, "dst": ev.src, "sport": ev.dport, "dport": ev.sport, "proto": ev.proto,
                          "pkts": ev.resp_pkts, "octets": max(40, ev.resp_bytes),
                          "first": ev.first_ts, "last": ev.last_ts, "flags": rflags})

    settings = Settings(internal_nets=tuple(internal_nets))
    meter = FlowMeter(settings, "conv", sink)
    reader = PcapReader(capture)
    for pkt in reader:
        meter.process(pkt)
    meter.flush()
    reader.close()
    return flows


def matches(alert, attack):
    if alert["threat_class"] != attack["threat_class"]:
        return False
    entities = {e for e in (attack.get("src"), attack.get("dst")) if e}
    if not entities & {alert["src"], alert["dst"]}:
        return False
    return attack["t0"] - 5 <= alert["event_time"] <= attack["t1"] + 300


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("capture")
    ap.add_argument("--report", default="results/flow-export-eval.json")
    args = ap.parse_args()
    truth = json.loads(Path(args.capture).with_suffix(".truth.json").read_text())

    flows = pcap_to_flows(args.capture, truth["internal_nets"])
    with tempfile.TemporaryDirectory() as tmp:
        nf = str(Path(tmp) / "lab.nfv5")
        base = int(min(f["first"] for f in flows))
        n = write_v5(nf, flows, base)
        settings = Settings(internal_nets=tuple(truth["internal_nets"]), data_dir=tmp)
        settings.exfil.allow_destinations = tuple(truth.get("allow_destinations", ()))
        store = Store(str(Path(tmp) / "fe.db"), SensorKey.load_or_create(tmp))
        engine = Engine(settings, store)
        summary = engine.run_flow_export(nf, label="flow-export-eval")
        alerts = store.list_alerts(limit=100000)
        chain = store.verify_chain()
        store.close()

    flow_attacks = [a for a in truth["attacks"] if a["threat_class"] in FLOW_CLASSES]
    detected = 0
    per = {}
    matched = set()
    for atk in flow_attacks:
        hits = [a for a in alerts if matches(a, atk)]
        ok = bool(hits)
        detected += ok
        per.setdefault(atk["threat_class"], {"attacks": 0, "detected": 0})
        per[atk["threat_class"]]["attacks"] += 1
        per[atk["threat_class"]]["detected"] += ok
        matched.update(a["alert_id"] for a in hits)
    false = [a for a in alerts if a["alert_id"] not in matched and a.get("category") != "-"
             and a["threat_class"] in FLOW_CLASSES]
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "capture": Path(args.capture).name,
        "mode": "flow-export (NetFlow v5)",
        "netflow_records": n,
        "flow_detectable_attacks": len(flow_attacks),
        "detected": detected,
        "recall_flow_classes": round(detected / len(flow_attacks), 3) if flow_attacks else None,
        "false_alerts_flow_classes": len(false),
        "per_class": per,
        "unavailable_in_flow_mode": ["dns.dga", "dns.tunnel", "tls.suspicious_session", "tls.known_bad_fingerprint"],
        "pipeline": {k: summary[k] for k in ("flows", "exports", "flows_per_s", "elapsed_s", "event_latency_ms_p99")},
        "custody_chain_ok": chain["ok"],
        "note": "DNS and TLS classes cannot fire without packet payload; this run measures only flow-observable classes.",
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"flow-export: {n} NetFlow v5 records, {detected}/{len(flow_attacks)} flow-detectable attacks, "
          f"{len(false)} false, chain_ok={chain['ok']}")
    for cls, r in sorted(per.items()):
        print(f"  {cls:<26} {r['detected']}/{r['attacks']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
