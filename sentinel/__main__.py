"""Command-line interface.

    python -m sentinel analyze capture.pcap [--realtime 1.0]
    tcpdump -i eth0 -U -w - | python -m sentinel analyze - --live
    python -m sentinel alerts [--limit 20]
    python -m sentinel verify-chain
    python -m sentinel bundle <alert_id> -o evidence.zip
    python -m sentinel verify-bundle evidence.zip [--capture capture.pcap] [--fingerprint SHA256]
    python -m sentinel schema
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from sentinel.config import Settings


def _open(args):
    from sentinel.custody import SensorKey
    from sentinel.store import Store

    settings = Settings.from_env()
    if args.data_dir:
        settings.data_dir = args.data_dir
    key = SensorKey.load_or_create(settings.data_dir)
    store = Store(str(Path(settings.data_dir) / "sentinel.db"), key)
    return settings, store


def cmd_analyze(args) -> int:
    from sentinel.engine import Engine

    settings, store = _open(args)
    engine = Engine(settings, store, dga_model_path=args.dga_model)
    summary = engine.run_capture(args.capture, label=args.label, realtime=args.realtime, live=args.live)
    alerts = store.list_alerts(limit=1000, source_id=summary["source_id"])
    if args.json:
        print(json.dumps({"summary": summary, "alerts": alerts}, indent=2, default=str))
    else:
        print(f"source {summary['source_id']}  status={summary['status']}  sha256={summary['capture_sha256']}")
        print(f"packets={summary['packets']} flows={summary['flows']} elapsed={summary['elapsed_s']}s "
              f"({summary['packets_per_s']} pkt/s, {summary['flows_per_s']} flows/s, {summary['mbit_per_s']} Mbit/s)")
        print(f"alerts={summary['alerts']}  alert latency p50={summary['alert_latency_ms_p50']} ms "
              f"p99={summary['alert_latency_ms_p99']} ms")
        for a in reversed(alerts):
            print(f"  [{a['severity']:>8}] {a['threat_class']:<26} conf={a['confidence']:.2f} "
                  f"{a['src']} -> {a['dst']}  {a['title']}  id={a['alert_id']}")
    store.close()
    return 0 if summary["status"] == "completed" else 1


def cmd_analyze_flows(args) -> int:
    from sentinel.engine import Engine

    settings, store = _open(args)
    engine = Engine(settings, store, dga_model_path=args.dga_model)
    summary = engine.run_flow_export(args.export, label=args.label)
    alerts = store.list_alerts(limit=1000, source_id=summary["source_id"])
    print(f"source {summary['source_id']}  status={summary['status']}  mode={summary['mode']}")
    print(f"flows={summary['flows']} exports={summary['exports']} elapsed={summary['elapsed_s']}s "
          f"({summary['flows_per_s']} flows/s)  alerts={summary['alerts']}")
    print(f"note: {summary['note']}")
    for a in reversed(alerts):
        print(f"  [{a['severity']:>8}] {a['threat_class']:<26} conf={a['confidence']:.2f} {a['src']} -> {a['dst']}")
    store.close()
    return 0 if summary["status"] == "completed" else 1


def cmd_export(args) -> int:
    from sentinel.export import export_alerts

    _, store = _open(args)
    alerts = store.list_alerts(limit=args.limit, threat_class=args.threat_class, severity=args.severity)
    body, _ = export_alerts(alerts, args.format, store_sensor_id(store))
    if args.output:
        Path(args.output).write_text(body, encoding="utf-8")
        print(f"wrote {len(alerts)} alerts to {args.output} as {args.format}")
    else:
        print(body)
    return 0


def store_sensor_id(store) -> str:
    from sentinel.config import Settings
    return Settings.from_env().sensor_id


def cmd_explain(args) -> int:
    from sentinel.explain import explain

    _, store = _open(args)
    alert = store.get_alert(args.alert_id)
    if alert is None:
        print(f"alert {args.alert_id} not found", file=sys.stderr)
        return 1
    result = explain(alert)
    print(result["text"])
    if result["next_steps"]:
        print("\nnext steps:")
        for step in result["next_steps"]:
            print(f"  - {step}")
    return 0


def cmd_hunt(args) -> int:
    from sentinel.archive import hunt

    settings, _ = _open(args)
    result = hunt(settings.data_dir, args.indicator, limit=args.limit)
    print(f"indicator {result['indicator']!r}: {len(result['matches'])} matching flows "
          f"(scanned {result['flows_scanned']} across {result['sources']} sources)")
    for m in result["matches"][:args.limit]:
        extra = f" sni={m['sni']}" if m.get("sni") else ""
        print(f"  {m['src']}:{m['sport']} -> {m['dst']}:{m['dport']} proto={m['proto']} "
              f"pkts={m['orig_pkts']} bytes={m['orig_bytes']} {m['state']}{extra}")
    return 0


def cmd_alerts(args) -> int:
    _, store = _open(args)
    for a in store.list_alerts(limit=args.limit):
        print(json.dumps(a) if args.json else
              f"{a['custody']['seq']:>6} [{a['severity']:>8}] {a['threat_class']:<26} {a['src']} -> {a['dst']}  {a['alert_id']}")
    return 0


def cmd_verify_chain(args) -> int:
    _, store = _open(args)
    result = store.verify_chain()
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


def cmd_bundle(args) -> int:
    from sentinel.evidence import build_bundle

    _, store = _open(args)
    data = build_bundle(store, args.alert_id)
    Path(args.output).write_bytes(data)
    print(f"wrote {args.output} ({len(data)} bytes)")
    return 0


def cmd_verify_bundle(args) -> int:
    from sentinel.evidence import verify_bundle

    result = verify_bundle(args.bundle, capture_path=args.capture, expected_key_fingerprint=args.fingerprint)
    for c in result["checks"]:
        print(f"  {'PASS' if c['ok'] else 'FAIL'}  {c['check']}{('  ' + c['detail']) if c['detail'] and not c['ok'] else ''}")
    print("VERIFIED" if result["ok"] else "NOT VERIFIED")
    return 0 if result["ok"] else 2


def cmd_schema(args) -> int:
    from sentinel.alerts import json_schema

    print(json.dumps(json_schema(), indent=2))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="sentinel", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", default=None, help="state directory (default: $SENTINEL_DATA_DIR or ./var)")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("analyze", help="process a capture file or a live pcap stream on stdin")
    p.add_argument("capture")
    p.add_argument("--label")
    p.add_argument("--realtime", type=float, default=None, help="replay speed multiplier (1.0 = original pacing)")
    p.add_argument("--live", action="store_true", help="fire timers on wall-clock time (for stdin streams)")
    p.add_argument("--dga-model", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("analyze-flows", help="process a NetFlow v5/v9 or IPFIX export file")
    p.add_argument("export")
    p.add_argument("--label")
    p.add_argument("--dga-model", default=None)
    p.set_defaults(func=cmd_analyze_flows)

    p = sub.add_parser("alerts", help="list stored alerts")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_alerts)

    p = sub.add_parser("export", help="export alerts as STIX 2.1, CEF, or JSONL")
    p.add_argument("format", choices=["stix", "cef", "jsonl"])
    p.add_argument("-o", "--output", default=None)
    p.add_argument("--limit", type=int, default=1000)
    p.add_argument("--threat-class", default=None)
    p.add_argument("--severity", default=None)
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("hunt", help="retro-hunt an indicator across the flow archive")
    p.add_argument("indicator")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_hunt)

    p = sub.add_parser("explain", help="print a deterministic explanation of an alert")
    p.add_argument("alert_id")
    p.set_defaults(func=cmd_explain)

    p = sub.add_parser("verify-chain", help="verify the signed hash chain over all stored alerts")
    p.set_defaults(func=cmd_verify_chain)

    p = sub.add_parser("bundle", help="export an evidence bundle for an alert")
    p.add_argument("alert_id")
    p.add_argument("-o", "--output", required=True)
    p.set_defaults(func=cmd_bundle)

    p = sub.add_parser("verify-bundle", help="verify an evidence bundle offline")
    p.add_argument("bundle")
    p.add_argument("--capture")
    p.add_argument("--fingerprint")
    p.set_defaults(func=cmd_verify_bundle)

    p = sub.add_parser("schema", help="print the alert JSON Schema")
    p.set_defaults(func=cmd_schema)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stderr)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
