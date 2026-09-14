"""Slow-HTTP, streaming anomaly, SPLT-in-TLS, and NetFlow/IPFIX flow-export ingest."""

import random

import pytest

from sentinel.config import Settings
from sentinel.custody import SensorKey
from sentinel.engine import Engine
from sentinel.ingest.flowmeter import FlowMeter
from sentinel.ingest.netflow import FlowExportReader
from sentinel.ingest.pcapio import RawPacket
from sentinel.lab import packets as P
from sentinel.lab.netflow_export import write_v5
from sentinel.store import Store


@pytest.fixture()
def engine(tmp_path):
    settings = Settings(internal_nets=("10.0.0.0/8", "10.20.0.0/16"), data_dir=str(tmp_path))
    store = Store(str(tmp_path / "t.db"), SensorKey.load_or_create(str(tmp_path)))
    eng = Engine(settings, store)
    eng.meter = FlowMeter(settings, "test", eng.handle)
    eng.ctx.source_id = "test"
    yield eng
    store.close()


class Feed:
    def __init__(self, engine):
        self.engine = engine
        self.i = 0

    def __call__(self, ts, frame):
        self.engine.meter.process(RawPacket(ts, frame, len(frame), 1, self.i, -1))
        self.i += 1

    def done(self):
        self.engine.meter.flush()
        return self.engine.store.list_alerts(limit=2000)


def classes(alerts):
    return sorted({a["threat_class"] for a in alerts})


def test_slowloris_detected(engine):
    feed, rng = Feed(engine), random.Random(1)
    target = "10.0.0.90"
    for k in range(50):
        src = f"10.0.11.{5 + k % 3}"
        sp = 30000 + k
        cseq, sseq = rng.randint(1, 2**31), rng.randint(1, 2**31)
        feed(100 + k * 0.05, P.tcp_packet(src, target, sp, 80, cseq, 0, P.SYN))
        feed(100 + k * 0.05 + 0.01, P.tcp_packet(target, src, 80, sp, sseq, cseq + 1, P.SYN | P.ACK))
        feed(100 + k * 0.05 + 0.02, P.tcp_packet(src, target, sp, 80, cseq + 1, sseq + 1, P.ACK))
        t = 102.0 + k * 0.05
        c = cseq + 1
        while t < 160:
            feed(t, P.tcp_packet(src, target, sp, 80, c, sseq + 1, P.PSH | P.ACK, b"X-a: b\r\n"))
            c += 7
            t += 15
    alerts = [a for a in feed.done() if a["threat_class"] == "ddos.slow_http"]
    assert len(alerts) >= 1
    a = alerts[0]
    assert a["dst"] == target
    ev = {e["feature"]: e["value"] for e in a["evidence"]}
    assert ev["concurrent_slow_connections"] >= 30 and ev["distinct_sources"] <= 8


def test_normal_web_traffic_is_not_slowloris(engine):
    feed, rng = Feed(engine), random.Random(2)
    target = "10.0.0.91"
    for k in range(80):
        src = f"10.0.{rng.randint(1,40)}.{rng.randint(1,254)}"
        sp = 30000 + k
        cseq, sseq = 100, 500
        feed(100 + k, P.tcp_packet(src, target, sp, 443, cseq, 0, P.SYN))
        feed(100 + k + 0.01, P.tcp_packet(target, src, 443, sp, sseq, cseq + 1, P.SYN | P.ACK))
        feed(100 + k + 0.02, P.tcp_packet(src, target, sp, 443, cseq + 1, sseq + 1, P.PSH | P.ACK, b"g" * 600))
        feed(100 + k + 0.05, P.tcp_packet(target, src, 443, sp, sseq + 1, cseq + 601, P.PSH | P.ACK, b"d" * 4000))
        feed(100 + k + 0.06, P.tcp_packet(src, target, sp, 443, cseq + 601, sseq + 4001, P.FIN | P.ACK))
        feed(100 + k + 0.07, P.tcp_packet(target, src, 443, sp, sseq + 4001, cseq + 602, P.FIN | P.ACK))
    assert "ddos.slow_http" not in classes(feed.done())


def test_tls_suspicious_carries_splt_evidence(engine):
    feed, rng = Feed(engine), random.Random(3)
    # warm up the TLS host population with benign browsers
    for h in range(25):
        src = f"10.20.30.{h + 1}"
        sp = 40000 + h
        hello = P.client_hello(P.CHROME_LIKE, "www.google.com", rng.randbytes)
        _tls_flow(feed, 10 + h, src, "142.250.1.1", sp, hello, up=400, down=8000)
    # an implant: rare Go fingerprint, no SNI, repeated to an unranked IP destination
    c2 = "185.220.9.9"
    for i in range(6):
        sp = 41000 + i
        hello = P.client_hello(P.GO_LIKE, None, rng.randbytes)
        _tls_flow(feed, 100 + i * 30, "10.20.5.50", c2, sp, hello, up=320, down=120)
    alerts = [a for a in feed.done() if a["threat_class"] == "tls.suspicious_session"]
    assert len(alerts) >= 1
    features = {e["feature"] for e in alerts[0]["evidence"]}
    assert "splt_packet_sizes" in features and "splt_direction_sequence" in features


def _tls_flow(feed, ts, src, dst, sp, hello, up, down):
    cseq, sseq = 1000, 5000
    feed(ts, P.tcp_packet(src, dst, sp, 443, cseq, 0, P.SYN))
    feed(ts + 0.01, P.tcp_packet(dst, src, 443, sp, sseq, cseq + 1, P.SYN | P.ACK))
    cseq += 1
    sseq += 1
    feed(ts + 0.011, P.tcp_packet(src, dst, sp, 443, cseq, sseq, P.ACK))
    feed(ts + 0.012, P.tcp_packet(src, dst, sp, 443, cseq, sseq, P.PSH | P.ACK, hello))
    cseq += len(hello)
    sh = P.server_hello()
    feed(ts + 0.02, P.tcp_packet(dst, src, 443, sp, sseq, cseq, P.PSH | P.ACK, sh))
    sseq += len(sh)
    feed(ts + 0.03, P.tcp_packet(src, dst, sp, 443, cseq, sseq, P.PSH | P.ACK, b"u" * up))
    feed(ts + 0.05, P.tcp_packet(dst, src, 443, sp, sseq, cseq + up, P.PSH | P.ACK, b"d" * down))
    feed(ts + 0.06, P.tcp_packet(src, dst, sp, 443, cseq + up, sseq + down, P.FIN | P.ACK))
    feed(ts + 0.07, P.tcp_packet(dst, src, 443, sp, sseq + down, cseq + up + 1, P.FIN | P.ACK))


def test_netflow_v5_roundtrip_and_scan_detection(tmp_path):
    settings = Settings(internal_nets=("10.0.0.0/8",), data_dir=str(tmp_path))
    store = Store(str(tmp_path / "f.db"), SensorKey.load_or_create(str(tmp_path)))
    engine = Engine(settings, store)
    flows = []
    base = 1_788_000_000
    # a horizontal/vertical scan: one source, 200 ports on one target, all rejected (1 pkt each)
    for i, port in enumerate(range(1, 201)):
        flows.append({"src": "10.0.9.9", "dst": "10.0.0.10", "sport": 40000 + i, "dport": port,
                      "proto": 6, "pkts": 1, "octets": 40, "first": base + i * 0.01,
                      "last": base + i * 0.01, "flags": P.SYN | P.RST})
    path = str(tmp_path / "scan.nfv5")
    n = write_v5(path, flows, base)
    assert n == 200
    reader = FlowExportReader("t")
    got = list(reader.read_file(path))
    assert len(got) == 200 and got[0].community_id.startswith("1:")
    summary = engine.run_flow_export(path, label="netflow-test")
    assert summary["mode"] == "flow-export" and summary["flows"] == 200
    alerts = [a for a in store.list_alerts(limit=100) if a["threat_class"] == "recon.scan"]
    assert len(alerts) == 1 and alerts[0]["src"] == "10.0.9.9"
    assert store.verify_chain()["ok"]
    store.close()


def test_netflow_v5_syn_flood_detection(tmp_path):
    settings = Settings(internal_nets=("10.0.0.0/8",), data_dir=str(tmp_path))
    store = Store(str(tmp_path / "f2.db"), SensorKey.load_or_create(str(tmp_path)))
    engine = Engine(settings, store)
    rng = random.Random(5)
    base = 1_788_000_000
    flows = []
    for s in range(4):
        for k in range(700):
            src = f"{rng.randint(11,200)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}"
            flows.append({"src": src, "dst": "10.0.0.80", "sport": rng.randint(1024, 65000), "dport": 443,
                          "proto": 6, "pkts": 1, "octets": 44, "first": base + s + k / 700,
                          "last": base + s + k / 700, "flags": P.SYN})
    path = str(tmp_path / "flood.nfv5")
    write_v5(path, flows, base)
    engine.run_flow_export(path)
    alerts = [a for a in store.list_alerts(limit=100) if a["threat_class"] == "ddos.syn_flood"]
    assert len(alerts) >= 1 and alerts[0]["dst"] == "10.0.0.80"
    store.close()


def test_anomaly_detector_flags_persistent_outlier(tmp_path):
    from sentinel.detect.anomaly import AnomalyDetector
    from sentinel.detect.base import Context
    from sentinel.events import FlowRecord

    settings = Settings(internal_nets=("10.0.0.0/8",), data_dir=str(tmp_path))
    det = AnomalyDetector(settings.anomaly)
    ctx = Context(settings, source_id="t")

    def flow(i, src, dst, dport, ob, rb, op, rp, dur):
        return FlowRecord(flow_id=f"f{i}", community_id=f"1:{i}", proto=6, src=src, sport=40000 + i, dst=dst,
                          dport=dport, first_ts=1000.0 + i, last_ts=1000.0 + i + dur, orig_pkts=op, orig_bytes=ob,
                          resp_pkts=rp, resp_bytes=rb, orig_payload=ob, resp_payload=rb, d_orig_bytes=ob,
                          d_resp_bytes=rb, first_export=True, final=True, state="closed")

    # train on a benign profile: small, balanced web-like flows
    rng = random.Random(7)
    alerts = []
    for i in range(1500):
        rec = flow(i, f"10.0.1.{rng.randint(1,254)}", "142.250.1.1", 443,
                   rng.randint(300, 1500), rng.randint(3000, 60000), rng.randint(4, 10),
                   rng.randint(6, 40), rng.uniform(0.1, 2))
        alerts += det.on_flow(rec, ctx)
    # one host now produces a persistent, very different profile (huge one-sided long UDP)
    for i in range(1500, 1560):
        rec = flow(i, "10.0.5.5", "45.9.9.9", 51820, 40_000_000, 0, 30000, 0, 1200.0)
        rec.proto = 17
        alerts += det.on_flow(rec, ctx)
    anomaly = [a for a in alerts if a.threat_class == "anomaly.behavioural"]
    assert anomaly and anomaly[0].src == "10.0.5.5"
    assert anomaly[0].confidence <= 0.7  # supporting signal, capped
