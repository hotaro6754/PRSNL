"""Detector behaviour on small, hand-built packet sequences (positives and benign look-alikes)."""

import base64
import random

import pytest

from sentinel.config import Settings
from sentinel.custody import SensorKey
from sentinel.engine import Engine
from sentinel.ingest.pcapio import RawPacket
from sentinel.ingest.flowmeter import FlowMeter
from sentinel.lab import packets as P
from sentinel.store import Store


@pytest.fixture()
def engine(tmp_path):
    settings = Settings(internal_nets=("10.0.0.0/8",), data_dir=str(tmp_path))
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
        return self.engine.store.list_alerts(limit=1000)


def classes(alerts):
    return sorted({a["threat_class"] for a in alerts})


def session(feed, ts, client, server, dport, sport, up=300, down=900, hello=None):
    feed(ts, P.tcp_packet(client, server, sport, dport, 100, 0, P.SYN))
    feed(ts + 0.01, P.tcp_packet(server, client, dport, sport, 500, 101, P.SYN | P.ACK))
    feed(ts + 0.011, P.tcp_packet(client, server, sport, dport, 101, 501, P.ACK))
    seq = 101
    if hello:
        feed(ts + 0.012, P.tcp_packet(client, server, sport, dport, seq, 501, P.PSH | P.ACK, hello))
        seq += len(hello)
    feed(ts + 0.02, P.tcp_packet(client, server, sport, dport, seq, 501, P.PSH | P.ACK, b"u" * up))
    feed(ts + 0.03, P.tcp_packet(server, client, dport, sport, 501, seq + up, P.PSH | P.ACK, b"d" * down))
    feed(ts + 0.04, P.tcp_packet(client, server, sport, dport, seq + up, 501 + down, P.FIN | P.ACK))
    feed(ts + 0.05, P.tcp_packet(server, client, dport, sport, 501 + down, seq + up + 1, P.FIN | P.ACK))


def test_spoofed_syn_flood(engine):
    feed, rng = Feed(engine), random.Random(1)
    for s in range(5):
        for k in range(1000):
            src = f"{rng.randint(11, 200)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
            feed(100 + s + k / 1000, P.tcp_packet(src, "10.0.0.80", rng.randint(1024, 65000), 443, k, 0, P.SYN))
    alerts = feed.done()
    flood = [a for a in alerts if a["threat_class"] == "ddos.syn_flood"]
    assert len(flood) == 1
    assert flood[0]["dst"] == "10.0.0.80" and "Spoofed" in flood[0]["title"]
    assert flood[0]["confidence"] >= 0.9


def test_busy_server_with_completed_handshakes_is_not_a_flood(engine):
    feed, rng = Feed(engine), random.Random(2)
    for s in range(6):
        for k in range(150):
            src = f"10.1.{rng.randint(0, 20)}.{rng.randint(1, 254)}"
            session(feed, 100 + s + k / 150, src, "10.0.0.81", 443, 20000 + (s * 150 + k) % 40000)
    assert not [a for a in feed.done() if a["threat_class"].startswith("ddos")]


def test_amplification(engine):
    feed, rng = Feed(engine), random.Random(3)
    reflectors = [f"{rng.randint(11, 200)}.{rng.randint(0, 255)}.1.{i % 250 + 1}" for i in range(100)]
    body = P.dns_response(1, "isc.org", 255, 0, [(P.DNS_TXT, P.txt_rdata("x" * 1000))])
    for s in range(5):
        for k in range(800):
            feed(10 + s + k / 800, P.udp_packet(reflectors[k % 100], "10.0.0.53", 53, 40000 + k, body))
    alerts = feed.done()
    assert "ddos.udp_amplification" in classes(alerts)


def test_vertical_scan_detected_by_sequential_test(engine):
    feed = Feed(engine)
    for i, port in enumerate(range(1, 200)):
        t = 50 + i * 0.01
        feed(t, P.tcp_packet("10.0.9.9", "10.0.0.10", 40000 + i, port, 1, 0, P.SYN))
        feed(t + 0.001, P.tcp_packet("10.0.0.10", "10.0.9.9", port, 40000 + i, 0, 2, P.RST | P.ACK))
    alerts = [a for a in feed.done() if a["threat_class"] == "recon.scan"]
    assert len(alerts) == 1 and alerts[0]["src"] == "10.0.9.9"
    llr = next(e for e in alerts[0]["evidence"] if e["feature"] == "trw_log_likelihood_ratio")
    assert llr["value"] >= llr["threshold"]


def test_successful_fanout_poller_is_not_a_scan(engine):
    feed = Feed(engine)
    for rnd in range(3):
        for k in range(80):
            session(feed, 10 + rnd * 300 + k * 0.05, "10.0.0.5", f"10.0.1.{k + 1}", 9100, 30000 + rnd * 100 + k)
    assert "recon.scan" not in classes(feed.done())


def test_syn_flood_does_not_turn_browsing_fanout_into_scans(engine):
    """Regression: unanswered spoofed SYNs once made the scan detector believe the tap was one-way,
    after which ordinary browsing to many CDN hosts was reported as horizontal scanning."""
    feed, rng = Feed(engine), random.Random(7)
    for k in range(3000):
        src = f"{rng.randint(11, 200)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
        feed(100 + k / 1000, P.tcp_packet(src, "10.0.0.80", rng.randint(1024, 65000), 443, k, 0, P.SYN))
    for k in range(70):
        session(feed, 110 + k * 2, "10.0.1.11", f"151.101.{k // 250}.{k + 1}", 443, 43000 + k)
    assert "recon.scan" not in classes(feed.done())


def test_jittered_beacon_detected(engine):
    feed, rng = Feed(engine), random.Random(4)
    t = 1000.0
    for i in range(14):
        session(feed, t, "10.0.5.23", "185.1.2.3", 443, 41000 + i, up=320, down=110)
        t += 60 * (1 + rng.uniform(-0.2, 0.2))
    alerts = [a for a in feed.done() if a["threat_class"] == "c2.beaconing"]
    assert len(alerts) == 1 and alerts[0]["dst"] == "185.1.2.3"


def test_irregular_browsing_is_not_beaconing(engine):
    feed, rng = Feed(engine), random.Random(5)
    t = 1000.0
    for i in range(30):
        session(feed, t, "10.0.5.24", "151.101.1.1", 443, 42000 + i, up=rng.randint(200, 3000), down=rng.randint(500, 60000))
        t += rng.expovariate(1 / 90)
    assert "c2.beaconing" not in classes(feed.done())


def _dns(feed, t, host, name, qtype=P.DNS_A, rcode=0, qid=1):
    sport = 50000 + qid % 10000
    feed(t, P.udp_packet(host, "10.0.0.2", sport, 53, P.dns_query(qid, name, qtype)))
    feed(t + 0.003, P.udp_packet("10.0.0.2", host, 53, sport, P.dns_response(qid, name, qtype, rcode)))


def test_dga_burst_detected(engine):
    feed = Feed(engine)
    names = ["qwxkzvbnrtplm.biz", "zxcvbnmlkjhgq.net", "pqzrxwvtkjhgf.info", "mnbvcxzlkjhgf.org", "xkqzjwvbpnrtl.com",
             "vbnmqwzxkjrtp.ru", "tlkjzxqwvbnmp.cc", "rtzxqvbnmlkpw.biz", "bnmzxqwtrvlkj.net", "kjhzxqwvbnrtp.info"]
    for i, name in enumerate(names):
        _dns(feed, 10 + i, "10.0.7.41", name, rcode=3, qid=i + 1)
    alerts = [a for a in feed.done() if a["threat_class"] == "dns.dga"]
    assert len(alerts) == 1 and alerts[0]["src"] == "10.0.7.41"
    assert alerts[0]["model"]["sha256"]


def test_popular_domains_never_score_as_dga(engine):
    feed = Feed(engine)
    for i, name in enumerate(["google.com", "facebook.com", "wikipedia.org", "microsoft.com", "amazon.com",
                              "cloudflare.com", "apple.com", "youtube.com", "linkedin.com", "github.com"]):
        _dns(feed, 10 + i, "10.0.7.42", name, qid=i + 1)
    assert "dns.dga" not in classes(feed.done())


def test_dns_tunnel_detected(engine):
    feed, rng = Feed(engine), random.Random(6)
    for i in range(120):
        chunk = base64.b32encode(rng.randbytes(35)).decode().rstrip("=").lower()
        _dns(feed, 10 + i * 0.3, "10.0.8.12", f"{chunk}.{i:04x}.t.exfil-lab.xyz", P.DNS_TXT, qid=i + 1)
    alerts = [a for a in feed.done() if a["threat_class"] == "dns.tunnel"]
    assert len(alerts) == 1 and alerts[0]["dst"] == "exfil-lab.xyz"


def test_exfiltration_with_both_directions(engine):
    feed = Feed(engine)
    c, s, sp = "10.0.6.77", "91.215.85.14", 45000
    feed(10.0, P.tcp_packet(c, s, sp, 443, 1, 0, P.SYN))
    feed(10.01, P.tcp_packet(s, c, 443, sp, 1, 2, P.SYN | P.ACK))
    seq = 2
    for i in range(20000):  # ~28 MB up, tiny down
        feed(10.02 + i * 0.001, P.tcp_packet(c, s, sp, 443, seq, 2, P.ACK, b"x" * 1400)[:128] if False else
             P.tcp_packet(c, s, sp, 443, seq, 2, P.ACK, b"x" * 1400))
        seq += 1400
        if i % 500 == 0:
            feed(10.02 + i * 0.001 + 0.0005, P.tcp_packet(s, c, 443, sp, 2, seq, P.ACK))
    alerts = [a for a in feed.done() if a["threat_class"] == "exfil.volume"]
    assert len(alerts) == 1
    ratio = next(e for e in alerts[0]["evidence"] if e["feature"] == "outbound_inbound_ratio")
    assert ratio["value"] > 100


def test_case_correlation_escalates_beacon_plus_tls(engine):
    from sentinel.alerts import Evidence, ThreatClass, Visibility, make_alert

    for cls in (ThreatClass.BEACONING, ThreatClass.TLS_SUSPICIOUS):
        alert = make_alert(cls, event_time=100.0, window_start=90.0, window_end=100.0, severity="high", confidence=0.8,
                           src="10.0.5.23", dst="185.1.2.3", evidence=[Evidence(feature="x", value=1)],
                           visibility=Visibility(directions_seen=2), detector="test/1")
        engine._emit(alert, 0.0)
    cases = engine.store.list_cases()
    assert len(cases) == 1
    assert cases[0]["severity"] == "critical" and cases[0]["alert_count"] == 2
