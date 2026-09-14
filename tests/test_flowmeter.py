from sentinel.config import Settings
from sentinel.events import DnsEvent, DstSecond, FlowRecord, TlsEvent
from sentinel.ingest.flowmeter import FlowMeter
from sentinel.ingest.pcapio import RawPacket
from sentinel.lab import packets as P

C, S = "10.1.1.10", "93.184.216.34"


class Harness:
    def __init__(self):
        self.events = []
        self.meter = FlowMeter(Settings(), "test", self.events.append)
        self.i = 0

    def send(self, ts, frame):
        self.meter.process(RawPacket(ts, frame, len(frame), 1, self.i, -1))
        self.i += 1

    def of(self, kind):
        return [e for e in self.events if isinstance(e, kind)]


def test_tcp_handshake_data_close_single_final_record():
    h = Harness()
    h.send(100.0, P.tcp_packet(C, S, 40000, 80, 1000, 0, P.SYN))
    h.send(100.1, P.tcp_packet(S, C, 80, 40000, 5000, 1001, P.SYN | P.ACK))
    h.send(100.2, P.tcp_packet(C, S, 40000, 80, 1001, 5001, P.ACK))
    h.send(100.3, P.tcp_packet(C, S, 40000, 80, 1001, 5001, P.PSH | P.ACK, b"GET / HTTP/1.1\r\n\r\n"))
    h.send(100.4, P.tcp_packet(S, C, 80, 40000, 5001, 1019, P.PSH | P.ACK, b"HTTP/1.1 200 OK\r\n\r\n" + b"a" * 500))
    h.send(100.5, P.tcp_packet(C, S, 40000, 80, 1019, 5520, P.FIN | P.ACK))
    h.send(100.6, P.tcp_packet(S, C, 80, 40000, 5520, 1020, P.FIN | P.ACK))
    h.send(110.0, P.udp_packet("10.9.9.9", "10.9.9.8", 1234, 9999, b"tick"))
    flows = [f for f in h.of(FlowRecord) if f.proto == 6]
    assert len(flows) == 1
    f = flows[0]
    assert (f.src, f.sport, f.dst, f.dport) == (C, 40000, S, 80)
    assert f.final and f.first_export and f.state == "closed"
    assert f.directions_seen == 2 and f.syn and f.synack
    assert f.orig_payload == 18 and f.resp_payload == 519
    assert f.community_id.startswith("1:")


def test_syn_without_reply_exported_as_attempt_after_timeout():
    h = Harness()
    h.send(50.0, P.tcp_packet(C, S, 40001, 22, 1, 0, P.SYN))
    h.send(54.0, P.udp_packet("10.9.9.9", "10.9.9.8", 1234, 9999, b"x"))
    assert not h.of(FlowRecord)
    h.send(56.5, P.udp_packet("10.9.9.9", "10.9.9.8", 1234, 9999, b"x"))
    attempts = [f for f in h.of(FlowRecord) if f.proto == 6]
    assert len(attempts) == 1 and attempts[0].state == "attempt" and attempts[0].directions_seen == 1


def test_rst_from_responder_is_rejected():
    h = Harness()
    h.send(1.0, P.tcp_packet(C, S, 40002, 23, 1, 0, P.SYN))
    h.send(1.1, P.tcp_packet(S, C, 23, 40002, 0, 2, P.RST | P.ACK))
    h.meter.flush()
    assert h.of(FlowRecord)[0].state == "rejected"


def test_dns_query_response_matched_and_nxdomain():
    h = Harness()
    h.send(10.0, P.udp_packet(C, "10.1.0.53", 53000, 53, P.dns_query(7, "xkqjzvbw.biz")))
    h.send(10.05, P.udp_packet("10.1.0.53", C, 53, 53000, P.dns_response(7, "xkqjzvbw.biz", rcode=3)))
    dns = h.of(DnsEvent)
    assert len(dns) == 1
    ev = dns[0]
    assert (ev.src, ev.dst, ev.qname, ev.rcode, ev.response_seen, ev.ts) == (C, "10.1.0.53", "xkqjzvbw.biz", 3, True, 10.0)


def test_dns_unanswered_query_emitted_after_wait():
    h = Harness()
    h.send(10.0, P.udp_packet(C, "10.1.0.53", 53001, 53, P.dns_query(8, "example.org", P.DNS_TXT)))
    h.meter.flush()
    ev = h.of(DnsEvent)[0]
    assert ev.rcode is None and not ev.response_seen and ev.qtype == P.DNS_TXT


def test_dns_response_only_when_query_direction_invisible():
    h = Harness()
    h.send(5.0, P.udp_packet("10.1.0.53", C, 53, 53002, P.dns_response(9, "example.net", answers=[(P.DNS_A, bytes([1, 2, 3, 4]))])))
    ev = h.of(DnsEvent)[0]
    assert ev.src == C and ev.answers == 1 and ev.rcode == 0


def test_sequence_gap_measured_as_loss():
    h = Harness()
    h.send(1.0, P.tcp_packet(C, S, 40003, 443, 100, 0, P.SYN))
    h.send(1.1, P.tcp_packet(S, C, 443, 40003, 900, 101, P.SYN | P.ACK))
    h.send(1.2, P.tcp_packet(C, S, 40003, 443, 101, 901, P.ACK, b"a" * 1000))
    h.send(1.3, P.tcp_packet(C, S, 40003, 443, 2101, 901, P.ACK, b"b" * 1000))  # 1000 bytes missing
    h.meter.flush()
    f = h.of(FlowRecord)[0]
    assert f.orig_gap_bytes == 1000
    assert abs(f.loss_ratio - 1000 / 3000) < 1e-9


def test_client_hello_split_across_segments_is_fingerprinted():
    h = Harness()
    record = P.client_hello(P.CHROME_LIKE, "mail.example.com")
    h.send(1.0, P.tcp_packet(C, S, 40004, 443, 10, 0, P.SYN))
    h.send(1.1, P.tcp_packet(S, C, 443, 40004, 50, 11, P.SYN | P.ACK))
    h.send(1.2, P.tcp_packet(C, S, 40004, 443, 11, 51, P.ACK))
    h.send(1.3, P.tcp_packet(C, S, 40004, 443, 11, 51, P.ACK, record[:200]))
    h.send(1.4, P.tcp_packet(C, S, 40004, 443, 211, 51, P.PSH | P.ACK, record[200:]))
    h.send(1.5, P.tcp_packet(S, C, 443, 40004, 51, 11 + len(record), P.PSH | P.ACK, P.server_hello()))
    tls_events = h.of(TlsEvent)
    assert len(tls_events) == 1
    assert tls_events[0].tls.ja4 == "t13d1516h2_8daaf6152771_e5627efa2ab1"
    assert tls_events[0].tls.sni == "mail.example.com"
    h.meter.flush()
    f = h.of(FlowRecord)[0]
    assert f.tls.server_hello_seen and f.tls.version == "TLS1.3" and f.tls.ja3s


def test_destination_second_aggregates_spoofed_syns():
    h = Harness()
    for i in range(300):
        h.send(20.0 + i / 1000, P.tcp_packet(f"198.51.{i // 250}.{i % 250 + 1}", "10.1.1.80", 1024 + i, 443, i, 0, P.SYN))
    h.send(21.2, P.udp_packet("10.9.9.9", "10.9.9.8", 1234, 9999, b"x"))
    stats = [s for s in h.of(DstSecond) if s.dst == "10.1.1.80"]
    assert len(stats) == 1
    assert stats[0].tcp_syn == 300 and len(stats[0].sources) == 300 and stats[0].ts == 20


def test_active_timeout_exports_increments():
    h = Harness()
    for i in range(14):
        ts = 1000.0 + i * 10
        h.send(ts, P.udp_packet(C, S, 50000, 4500, b"u" * 100))
        h.send(ts + 0.01, P.udp_packet(S, C, 4500, 50000, b"d" * 50))
    h.meter.flush()
    records = [f for f in h.of(FlowRecord) if f.dport == 4500]
    assert len(records) >= 3
    assert sum(r.first_export for r in records) == 1
    assert sum(r.d_orig_bytes for r in records) == records[-1].orig_bytes
    assert records[-1].final
