"""Throughput and latency benchmark (PS 26145 constraint d).

1. Maximum throughput on a capture: packets are fed as fast as the pipeline can
   take them (ingest -> flow metering -> every detector -> signed alert store).

2. Steady-rate ladder (the stated target): uniform benign sessions (DNS lookup,
   TCP handshake, TLS ClientHello on a share of sessions, request/response
   data, close) are generated for each offered rate and released on their own
   timestamps against the wall clock. Lag = how late each packet is processed
   versus its release time. A rate is SUSTAINED when p99 lag < 0.5 s and the
   lag at the end of the run < 1 s. The stated target is the highest sustained
   rate. Bursty captures are deliberately not used for this: their average rate
   hides peaks many times higher.

    python ml/benchmark.py lab/captures/lab-30m.pcap --rates 500 1000 2000 3000 --seconds 20
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import random
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentinel import __version__  # noqa: E402
from sentinel.config import Settings  # noqa: E402
from sentinel.custody import SensorKey  # noqa: E402
from sentinel.engine import Engine  # noqa: E402
from sentinel.ingest.flowmeter import FlowMeter  # noqa: E402
from sentinel.ingest.pcapio import RawPacket  # noqa: E402
from sentinel.lab import packets as P  # noqa: E402
from sentinel.store import Store  # noqa: E402


def _engine(tmp: str, internal=("10.0.0.0/8",)) -> tuple[Engine, Store]:
    settings = Settings(internal_nets=tuple(internal), data_dir=tmp)
    store = Store(str(Path(tmp) / "bench.db"), SensorKey.load_or_create(tmp))
    return Engine(settings, store), store


def max_throughput(capture: str) -> dict:
    truth_path = Path(capture).with_suffix(".truth.json")
    internal = json.loads(truth_path.read_text())["internal_nets"] if truth_path.exists() else ["10.0.0.0/8"]
    with tempfile.TemporaryDirectory() as tmp:
        engine, store = _engine(tmp, internal)
        summary = engine.run_capture(capture, label="benchmark-max")
        store.close()
    return {"capture": Path(capture).name,
            **{k: summary[k] for k in ("packets", "bytes", "flows", "elapsed_s", "packets_per_s", "flows_per_s",
                                       "mbit_per_s", "alerts", "event_latency_ms_p50", "event_latency_ms_p99")}}


def steady_packets(flows_per_s: int, seconds: int, seed: int = 26145) -> tuple[list[RawPacket], int]:
    rng = random.Random(seed)
    clients = [f"10.30.{i // 250}.{i % 250 + 1}" for i in range(2000)]
    servers = [f"151.{101 + i // 250}.{i % 250 + 1}.10" for i in range(1500)]
    resolver = "10.30.255.53"
    hello = P.client_hello(P.CHROME_LIKE, "www.example.com", rng.randbytes)
    events: list[tuple[float, bytes]] = []
    n = flows_per_s * seconds
    for k in range(n):
        t = k / flows_per_s
        c, s = clients[k % len(clients)], servers[rng.randrange(len(servers))]
        sp = 20000 + k % 40000
        qid = k & 0xFFFF
        events.append((t, P.udp_packet(c, resolver, sp, 53, P.dns_query(qid, f"host{k % 5000}.example.com"))))
        events.append((t + 0.002, P.udp_packet(resolver, c, 53, sp, P.dns_response(qid, f"host{k % 5000}.example.com"))))
        t += 0.003
        seq, ack = 1000, 5000
        events.append((t, P.tcp_packet(c, s, sp, 443, seq, 0, P.SYN)))
        events.append((t + 0.01, P.tcp_packet(s, c, 443, sp, ack, seq + 1, P.SYN | P.ACK)))
        seq += 1
        ack += 1
        events.append((t + 0.011, P.tcp_packet(c, s, sp, 443, seq, ack, P.ACK)))
        if k % 5 == 0:
            events.append((t + 0.012, P.tcp_packet(c, s, sp, 443, seq, ack, P.PSH | P.ACK, hello)))
            seq += len(hello)
        up, down = rng.randint(300, 1200), rng.randint(800, 1400)
        events.append((t + 0.03, P.tcp_packet(c, s, sp, 443, seq, ack, P.PSH | P.ACK, b"u" * up)))
        events.append((t + 0.05, P.tcp_packet(s, c, 443, sp, ack, seq + up, P.PSH | P.ACK, b"d" * down)))
        events.append((t + 0.051, P.tcp_packet(s, c, 443, sp, ack + down, seq + up, P.PSH | P.ACK, b"d" * down)))
        events.append((t + 0.06, P.tcp_packet(c, s, sp, 443, seq + up, ack + 2 * down, P.FIN | P.ACK)))
        events.append((t + 0.07, P.tcp_packet(s, c, 443, sp, ack + 2 * down, seq + up + 1, P.FIN | P.ACK)))
        events.append((t + 0.071, P.tcp_packet(c, s, sp, 443, seq + up + 1, ack + 2 * down + 1, P.ACK)))
    events.sort(key=lambda e: e[0])
    base = 1_790_000_000.0
    packets = [RawPacket(base + t, frame, len(frame), 1, i, -1) for i, (t, frame) in enumerate(events)]
    return packets, n


def steady(flows_per_s: int, seconds: int) -> dict:
    packets, flows = steady_packets(flows_per_s, seconds)
    total_bytes = sum(p.wire_len for p in packets)
    with tempfile.TemporaryDirectory() as tmp:
        engine, store = _engine(tmp)
        meter = FlowMeter(engine.settings, "steady", engine.handle)
        engine.ctx.source_id = "steady"
        first = packets[0].ts
        lags = []
        wall0 = time.perf_counter()
        lag = 0.0
        for i, pkt in enumerate(packets):
            due = wall0 + (pkt.ts - first)
            now = time.perf_counter()
            if due > now:
                time.sleep(due - now)
                now = time.perf_counter()
            meter.process(pkt)
            lag = time.perf_counter() - due
            if i % 50 == 0:
                lags.append(lag)
        final_lag = lag
        meter.flush()
        alerts = engine.alerts_emitted
        store.close()
    lags.sort()
    span = packets[-1].ts - first
    p99 = lags[int(0.99 * (len(lags) - 1))]
    return {
        "offered_flows_per_s": flows_per_s,
        "offered_packets_per_s": round(len(packets) / span, 1),
        "offered_mbit_per_s": round(total_bytes * 8 / span / 1e6, 2),
        "seconds": seconds,
        "packets": len(packets),
        "flows": flows,
        "lag_s_p50": round(lags[len(lags) // 2], 4),
        "lag_s_p99": round(p99, 4),
        "lag_s_max": round(lags[-1], 4),
        "lag_s_final": round(final_lag, 4),
        "sustained": p99 < 0.5 and final_lag < 1.0,
        "alerts": alerts,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("capture", nargs="?")
    ap.add_argument("--rates", type=int, nargs="*", default=[500, 1000, 2000, 3000, 4000])
    ap.add_argument("--seconds", type=int, default=20)
    ap.add_argument("--report", default="results/benchmark.json")
    args = ap.parse_args()

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sentinel_version": __version__,
        "host": {"platform": platform.platform(), "processor": platform.processor(), "cpus": os.cpu_count(),
                 "python": platform.python_version()},
        "mode": "single process on one core; all detectors enabled; alerts signed and persisted",
        "sustained_rule": "p99 packet lag < 0.5 s and lag at end of run < 1 s",
        "max_throughput": max_throughput(args.capture) if args.capture else None,
        "steady": [],
    }
    if report["max_throughput"]:
        print(json.dumps(report["max_throughput"]))
    for rate in args.rates:
        row = steady(rate, args.seconds)
        report["steady"].append(row)
        print(json.dumps(row))
    sustained = [r for r in report["steady"] if r["sustained"]]
    report["stated_target"] = max(sustained, key=lambda r: r["offered_flows_per_s"]) if sustained else None
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    t = report["stated_target"]
    print("stated target:", f"{t['offered_flows_per_s']} flows/s, {t['offered_packets_per_s']} pkt/s, "
                            f"{t['offered_mbit_per_s']} Mbit/s sustained" if t else "none sustained")
    return 0


if __name__ == "__main__":
    sys.exit(main())
