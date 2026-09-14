"""Records passed from ingest to detection. Plain slotted dataclasses: they are
created per packet/flow and must stay cheap."""

from __future__ import annotations

from dataclasses import dataclass, field

TCP, UDP, ICMP, ICMP6 = 6, 17, 1, 58


@dataclass(slots=True)
class PacketRef:
    """Where a packet lives in its source capture (for evidence extraction)."""

    source_id: str
    index: int
    offset: int  # byte offset of the record header in a classic pcap; -1 when unknown (pcapng, Zeek)


@dataclass(slots=True)
class TlsInfo:
    version: str | None = None  # negotiated if ServerHello seen, else offered maximum
    sni: str | None = None
    alpn: str | None = None
    ja3: str | None = None
    ja3_string: str | None = None
    ja4: str | None = None
    ja3s: str | None = None
    server_hello_seen: bool = False


@dataclass(slots=True)
class DnsEvent:
    ts: float
    src: str
    dst: str
    qname: str
    qtype: int
    rcode: int | None  # None when the response was not observed
    answers: int
    response_seen: bool
    flow_id: str
    community_id: str = ""
    ref: PacketRef | None = None


@dataclass(slots=True)
class TlsEvent:
    ts: float
    src: str
    sport: int
    dst: str
    dport: int
    flow_id: str
    tls: TlsInfo
    community_id: str = ""
    ref: PacketRef | None = None


@dataclass(slots=True)
class DstSecond:
    """Per-destination packet aggregates for one second of event time."""

    ts: int
    dst: str
    packets: int = 0
    bytes: int = 0
    tcp_syn: int = 0  # SYN without ACK toward dst
    synack_sent: int = 0  # SYN+ACK sent by dst (needs reverse direction visible)
    udp_packets: int = 0
    udp_sent: int = 0  # UDP packets sent BY this host in the same second (a busy server answers, a flood victim cannot)
    amp_bytes: int = 0  # UDP bytes toward dst from amplification service ports
    amp_packets: int = 0
    amp_requests_sent: int = 0  # UDP packets dst sent to amplification ports
    sources: dict = field(default_factory=dict)  # src -> packets (capped)
    amp_sources: set = field(default_factory=set)
    sources_truncated: bool = False


@dataclass(slots=True)
class FlowRecord:
    """A bidirectional flow export. Long flows are exported more than once
    (active timeout); the d_* fields carry the increment since the previous export."""

    flow_id: str
    community_id: str
    proto: int
    src: str
    sport: int
    dst: str
    dport: int
    first_ts: float
    last_ts: float
    orig_pkts: int
    orig_bytes: int
    resp_pkts: int
    resp_bytes: int
    orig_payload: int
    resp_payload: int
    d_orig_bytes: int
    d_resp_bytes: int
    first_export: bool
    final: bool
    state: str  # attempt | established | rejected | closed | udp | other
    syn: bool = False
    synack: bool = False
    rst_from_resp: bool = False
    orig_inferred: bool = False  # originator guessed (flow picked up mid-stream)
    orig_gap_bytes: int = 0
    resp_gap_bytes: int = 0
    tls: TlsInfo | None = None
    quic_version: int | None = None
    splt: list = field(default_factory=list)  # (signed payload length, inter-arrival ms)
    first_ref: PacketRef | None = None
    last_ref: PacketRef | None = None
    source: str = "pcap"

    @property
    def directions_seen(self) -> int:
        return (1 if self.orig_pkts else 0) + (1 if self.resp_pkts else 0)

    @property
    def loss_ratio(self) -> float:
        seen = self.orig_payload + self.resp_payload
        gaps = self.orig_gap_bytes + self.resp_gap_bytes
        return gaps / (seen + gaps) if (seen + gaps) else 0.0
