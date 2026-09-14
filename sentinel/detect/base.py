"""Detector interface and shared helpers."""

from __future__ import annotations

import math
from collections import Counter, OrderedDict
from dataclasses import dataclass, field

from sentinel.alerts import Alert, Custody, EvidenceScope, PacketPointer, Visibility
from sentinel.config import Settings
from sentinel.events import DnsEvent, DstSecond, FlowRecord, PacketRef, TlsEvent


@dataclass
class Context:
    """State shared by detectors: settings, event clock and network-wide prevalence."""

    settings: Settings
    source_id: str = "unknown"
    now: float = 0.0
    ja4_hosts: dict = field(default_factory=dict)  # ja4 -> set(internal hosts), capped
    domain_hosts: dict = field(default_factory=dict)  # registered domain -> set(hosts), capped
    dst_first_seen: dict = field(default_factory=dict)  # external ip -> first event time
    tranco_rank: object = None  # callable(registered_domain) -> rank | None

    def note_ja4(self, ja4: str, host: str) -> int:
        hosts = self.ja4_hosts.setdefault(ja4, set())
        if len(hosts) < 64:
            hosts.add(host)
        return len(hosts)

    def note_domain(self, domain: str, host: str) -> int:
        hosts = self.domain_hosts.setdefault(domain, set())
        if len(hosts) < 64:
            hosts.add(host)
        return len(hosts)


class Detector:
    name = "detector"
    version = "1"

    def on_flow(self, rec: FlowRecord, ctx: Context) -> list[Alert]:
        return []

    def on_dns(self, ev: DnsEvent, ctx: Context) -> list[Alert]:
        return []

    def on_tls(self, ev: TlsEvent, ctx: Context) -> list[Alert]:
        return []

    def on_dst_second(self, st: DstSecond, ctx: Context) -> list[Alert]:
        return []

    def on_tick(self, now: float, ctx: Context) -> list[Alert]:
        return []

    @property
    def detector_id(self) -> str:
        return f"{self.name}/{self.version}"


class Cooldown:
    """Suppress repeat alerts for the same key within a period (bounded memory)."""

    def __init__(self, period: float, max_keys: int = 100_000) -> None:
        self.period = period
        self.max_keys = max_keys
        self._last: OrderedDict = OrderedDict()

    def allow(self, key, now: float) -> bool:
        last = self._last.get(key)
        if last is not None and now - last < self.period:
            return False
        self._last[key] = now
        self._last.move_to_end(key)
        while len(self._last) > self.max_keys:
            self._last.popitem(last=False)
        return True


def normalised_entropy(counts) -> float:
    """Shannon entropy of a frequency table divided by its maximum (0..1)."""
    values = list(counts.values()) if isinstance(counts, (dict, Counter)) else list(counts)
    n = len(values)
    total = sum(values)
    if n <= 1 or total == 0:
        return 0.0
    h = -sum((v / total) * math.log2(v / total) for v in values if v)
    return h / math.log2(n)


def string_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def visibility_of(flows: list[FlowRecord], needs_both_directions: bool = False) -> Visibility:
    if not flows:
        return Visibility(directions_seen=1.0, handshake_seen=None, est_loss_pct=0.0, sufficient=not needs_both_directions)
    directions = sum(f.directions_seen for f in flows) / len(flows)
    tcp = [f for f in flows if f.proto == 6]
    handshake = any(f.syn and f.synack for f in tcp) if tcp else None
    seen = sum(f.orig_payload + f.resp_payload for f in flows)
    gaps = sum(f.orig_gap_bytes + f.resp_gap_bytes for f in flows)
    loss = 100.0 * gaps / (seen + gaps) if seen + gaps else 0.0
    sufficient = not needs_both_directions or directions >= 1.99
    note = None
    if needs_both_directions and not sufficient:
        note = "only one direction of this traffic was visible; ratio-based evidence is incomplete"
    elif loss > 1.0:
        note = f"capture loss estimated at {loss:.1f}% from TCP sequence gaps"
    return Visibility(directions_seen=round(directions, 2), handshake_seen=handshake,
                      est_loss_pct=round(loss, 3), sufficient=sufficient, note=note)


def visibility_discount(vis: Visibility) -> float:
    """Confidence multiplier for degraded visibility."""
    factor = 1.0
    if not vis.sufficient:
        factor *= 0.5
    if vis.est_loss_pct > 5:
        factor *= 0.8
    elif vis.est_loss_pct > 1:
        factor *= 0.9
    return factor


def custody_for(ctx: Context, refs: list[PacketRef | None], scope: EvidenceScope | None) -> Custody:
    pointers = []
    seen = set()
    for ref in refs:
        if ref is None or ref.index in seen:
            continue
        seen.add(ref.index)
        pointers.append(PacketPointer(index=ref.index, offset=ref.offset))
        if len(pointers) >= 64:
            break
    return Custody(source_id=ctx.source_id, packets=pointers, scope=scope)


def scope_for_flows(flows: list[FlowRecord], hosts: list[str] | None = None, max_packets: int = 5000) -> EvidenceScope:
    offsets = [r.offset for f in flows for r in (f.first_ref, f.last_ref) if r is not None and r.offset >= 0]
    ports = sorted({p for f in flows for p in (f.dport,) if p})[:32]
    protos = {f.proto for f in flows}
    return EvidenceScope(
        hosts=hosts if hosts is not None else sorted({h for f in flows for h in (f.src, f.dst)})[:32],
        ports=ports,
        proto=protos.pop() if len(protos) == 1 else None,
        t0=min(f.first_ts for f in flows),
        t1=max(f.last_ts for f in flows),
        offset_lo=min(offsets) if offsets else -1,
        offset_hi=max(offsets) if offsets else -1,
        max_packets=max_packets,
    )
