import random
import struct

import pytest

from sentinel.config import Settings
from sentinel.custody import SensorKey
from sentinel.engine import Engine
from sentinel.ingest.flowmeter import FlowMeter
from sentinel.ingest.pcapio import RawPacket
from sentinel.lab import packets as P
from sentinel.proto import dns


def test_parse_query_and_response():
    q = dns.parse(P.dns_query(0x1234, "Mail.Example.COM", P.DNS_TXT))
    assert q == dns.DnsMessage(0x1234, False, 0, "mail.example.com", P.DNS_TXT, 0)
    r = dns.parse(P.dns_response(7, "x.test", P.DNS_A, 3))
    assert r.is_response and r.rcode == 3 and r.answers == 0


def test_parse_compressed_question_name():
    header = struct.pack("!HHHHHH", 1, 0x0100, 1, 0, 0, 0)
    # Question "a" + pointer to offset 20, where "example.com" is stored after qtype/qclass (offsets 16-19).
    msg = header + b"\x01a\xc0\x14" + struct.pack("!HH", 28, 1) + b"\x07example\x03com\x00"
    parsed = dns.parse(msg)
    assert parsed is not None and parsed.qname == "a.example.com" and parsed.qtype == 28
    # A pointer loop must terminate and be rejected.
    assert dns.parse(header + b"\x01a\xc0\x0e" + struct.pack("!HH", 1, 1)) is None


@pytest.mark.parametrize("payload", [b"", b"\x00" * 11, struct.pack("!HHHHHH", 1, 0, 0, 0, 0, 0) + b"\x00\x00\x01\x00\x01",
                                     struct.pack("!HHHHHH", 1, 0, 1, 0, 0, 0) + b"\x40" + b"a" * 64,
                                     struct.pack("!HHHHHH", 1, 0, 1, 0, 0, 0) + b"\xc0\x0c\x00\x01\x00\x01"])
def test_parse_rejects_malformed(payload):
    assert dns.parse(payload) is None


def test_busy_resolver_is_not_a_udp_flood(tmp_path):
    settings = Settings(internal_nets=("10.0.0.0/8",), data_dir=str(tmp_path))
    from sentinel.store import Store

    store = Store(str(tmp_path / "t.db"), SensorKey.load_or_create(str(tmp_path)))
    engine = Engine(settings, store)
    meter = FlowMeter(settings, "t", engine.handle)
    rng = random.Random(1)
    i = 0
    for s in range(6):
        for k in range(4000):
            ts = 100 + s + k / 4000
            client = f"10.1.{rng.randint(0, 20)}.{rng.randint(1, 250)}"
            sport = 1024 + (k % 60000)
            for frame in (P.udp_packet(client, "10.0.0.53", sport, 53, P.dns_query(k & 0xFFFF, "a.example.com")),
                          P.udp_packet("10.0.0.53", client, 53, sport, P.dns_response(k & 0xFFFF, "a.example.com"))):
                meter.process(RawPacket(ts, frame, len(frame), 1, i, -1))
                i += 1
    meter.flush()
    assert not [a for a in store.list_alerts(limit=100) if a["threat_class"].startswith("ddos")]
    store.close()


def test_unanswered_udp_flood_still_detected(tmp_path):
    settings = Settings(internal_nets=("10.0.0.0/8",), data_dir=str(tmp_path))
    from sentinel.store import Store

    store = Store(str(tmp_path / "t.db"), SensorKey.load_or_create(str(tmp_path)))
    engine = Engine(settings, store)
    meter = FlowMeter(settings, "t", engine.handle)
    rng = random.Random(2)
    i = 0
    for s in range(5):
        for k in range(4000):
            src = f"{rng.randint(11, 200)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
            frame = P.udp_packet(src, "10.0.0.90", rng.randint(1024, 65000), 5060, b"x" * 64)
            meter.process(RawPacket(100 + s + k / 4000, frame, len(frame), 1, i, -1))
            i += 1
    meter.flush()
    assert "ddos.udp_flood" in {a["threat_class"] for a in store.list_alerts(limit=100)}
    store.close()
