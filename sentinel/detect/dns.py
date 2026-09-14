"""(c) DGA domains and DNS tunnelling from DNS metadata.

DGA: a character n-gram model scores each registrable label; an alert needs
several distinct high-probability domains from one host inside a window, which
is how DGA malware behaves (it tries many names until one resolves). Popular
domains (Tranco list, or queried by many internal hosts) are excluded.

Tunnelling: per (host, registered domain) window, many unique subdomains, long
high-entropy labels and a large encoded payload, with TXT/NULL/CNAME/MX use as
supporting evidence.
"""

from __future__ import annotations

from collections import Counter, deque
from functools import lru_cache
from math import log2

import tldextract

from sentinel.alerts import Evidence, EvidenceScope, ThreatClass, Visibility, make_alert, severity_for
from sentinel.config import DnsSettings
from sentinel.detect.base import Context, Cooldown, Detector, custody_for
from sentinel.detect.dga_model import DgaModel
from sentinel.events import DnsEvent
from sentinel.intel.toplist import TopList

_EXTRACT = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)  # bundled public suffix snapshot, no network
_SKIP_SUFFIXES = ("arpa", "local", "lan", "internal", "localdomain", "home", "corp", "test", "invalid", "localhost")
_RECORD_NAMES = {1: "A", 2: "NS", 5: "CNAME", 10: "NULL", 12: "PTR", 15: "MX", 16: "TXT", 28: "AAAA", 33: "SRV",
                 65: "HTTPS", 255: "ANY"}
_TUNNEL_TYPES = {5, 10, 15, 16}

_DGA_ADVISORY = [
    "Isolate the source host for endpoint investigation through the operator's out-of-band process.",
    "Sinkhole or block the resolving domain at the production resolver if it is confirmed malicious.",
]
_TUNNEL_ADVISORY = [
    "Treat the domain as a possible data channel: review what the source host could access.",
    "Restrict recursive resolution for this domain at the production resolver after confirmation.",
]


@lru_cache(maxsize=262_144)
def split_name(qname: str) -> tuple[str, str, str]:
    """Return (subdomain, registrable label, registered domain); empty strings if not a public name."""
    parts = _EXTRACT(qname)
    if not parts.suffix or not parts.domain:
        return "", "", ""
    if parts.suffix.split(".")[-1] in _SKIP_SUFFIXES:
        return "", "", ""
    return parts.subdomain, parts.domain, f"{parts.domain}.{parts.suffix}"


class _Tunnel:
    __slots__ = ("start", "last", "queries", "subs", "chars", "total_chars", "label_sum", "max_label", "qtypes",
                 "nxdomain", "events", "examples")

    def __init__(self, ts: float) -> None:
        self.start = self.last = ts
        self.queries = 0
        self.subs: set = set()
        self.chars: Counter = Counter()
        self.total_chars = 0
        self.label_sum = 0
        self.max_label = 0
        self.qtypes: Counter = Counter()
        self.nxdomain = 0
        self.events: deque = deque(maxlen=24)
        self.examples: list = []


class DnsDetector(Detector):
    name = "dns"
    version = "2.0"

    def __init__(self, settings: DnsSettings, model: DgaModel | None, toplist: TopList | None) -> None:
        self.s = settings
        self.model = model
        self.toplist = toplist or TopList({}, "none")
        self.dga_cooldown = Cooldown(settings.cooldown_s)
        self.tunnel_cooldown = Cooldown(settings.cooldown_s)
        self._dga_hits: dict[str, deque] = {}
        self._tunnels: dict[tuple, _Tunnel] = {}
        self._last_gc = 0.0

    def on_dns(self, ev: DnsEvent, ctx: Context) -> list:
        if ev.qtype == 12:
            return []
        sub, label, registered = split_name(ev.qname)
        if not registered:
            return []
        hosts_for_domain = ctx.note_domain(registered, ev.src)
        popular = hosts_for_domain >= self.s.popular_domain_hosts or self.toplist.rank(registered) is not None
        alerts = []
        if sub and not popular:
            alerts += self._tunnel(ev, sub, registered, ctx)
        if self.model is not None and not popular and len(label) >= 6:
            probability = self.model.probability(label)
            if probability >= self.s.dga_probability:
                alerts += self._dga(ev, registered, probability, ctx)
        self._gc(ev.ts)
        return alerts

    # ------------------------------------------------------------------- DGA
    def _dga(self, ev: DnsEvent, registered: str, probability: float, ctx: Context) -> list:
        s = self.s
        hits = self._dga_hits.setdefault(ev.src, deque(maxlen=256))
        while hits and ev.ts - hits[0][0] > s.dga_window_s:
            hits.popleft()
        if any(h[2] == registered for h in hits):
            return []
        hits.append((ev.ts, ev, registered, probability))
        if len(hits) < s.dga_min_domains or not self.dga_cooldown.allow(ev.src, ev.ts):
            return []
        events = [h[1] for h in hits]
        answered = [e for e in events if e.rcode is not None]
        nx = sum(1 for e in answered if e.rcode == 3)
        nx_ratio = nx / len(answered) if answered else None
        mean_p = sum(h[3] for h in hits) / len(hits)
        confidence = 0.5 * mean_p + 0.3 * min(1.0, len(hits) / (2 * s.dga_min_domains)) \
            + 0.2 * (nx_ratio if nx_ratio is not None else 0.5)
        confidence = round(min(0.97, confidence), 3)
        visibility = Visibility(
            directions_seen=2.0 if answered else 1.0, handshake_seen=None, sufficient=True,
            note=None if answered else "DNS responses were not visible, so NXDOMAIN evidence is unavailable",
        )
        evidence = [
            Evidence(feature="distinct_dga_like_domains", value=len(hits), threshold=s.dga_min_domains,
                     note=f"within {int(s.dga_window_s)} s"),
            Evidence(feature="mean_model_probability", value=round(mean_p, 3), threshold=s.dga_probability),
            Evidence(feature="nxdomain_ratio", value=round(nx_ratio, 3) if nx_ratio is not None else None,
                     note=f"{nx} of {len(answered)} answered lookups failed" if answered else "responses not visible"),
            Evidence(feature="example_domains", value=[e.qname for e in events[-8:]]),
            Evidence(feature="resolver", value=sorted({e.dst for e in events})[:4]),
        ]
        scope = EvidenceScope(hosts=[ev.src], ports=[53], proto=17, t0=events[0].ts, t1=ev.ts + 3, max_packets=2000)
        return [make_alert(
            ThreatClass.DGA, sensor_id=ctx.settings.sensor_id, event_time=ev.ts, window_start=events[0].ts,
            window_end=ev.ts, severity=severity_for(confidence, "high"), confidence=confidence,
            src=ev.src, dst=events[-1].qname, flow_ids=sorted({e.community_id for e in events if e.community_id}),
            evidence=evidence, visibility=visibility, detector=self.detector_id, model=self.model.ref(),
            custody=custody_for(ctx, [e.ref for e in events], scope), advisory=_DGA_ADVISORY,
        )]

    # ---------------------------------------------------------------- tunnel
    def _tunnel(self, ev: DnsEvent, sub: str, registered: str, ctx: Context) -> list:
        s = self.s
        key = (ev.src, registered)
        st = self._tunnels.get(key)
        if st is None or ev.ts - st.start > s.tunnel_window_s:
            st = self._tunnels[key] = _Tunnel(ev.ts)
        st.queries += 1
        st.last = ev.ts
        st.qtypes[ev.qtype] += 1
        if ev.rcode == 3:
            st.nxdomain += 1
        longest = max(len(part) for part in sub.split("."))
        st.label_sum += longest
        st.max_label = max(st.max_label, longest)
        if sub not in st.subs and len(st.subs) < 4096:
            st.subs.add(sub)
            flat = sub.replace(".", "")
            st.total_chars += len(flat)
            st.chars.update(flat)
            if len(st.examples) < 3:
                st.examples.append(ev.qname[:120])
        st.events.append(ev)
        if len(st.subs) < s.tunnel_min_unique_subdomains or st.total_chars < s.tunnel_min_payload_chars:
            return []
        mean_label = st.label_sum / st.queries
        total = sum(st.chars.values())
        entropy = -sum((c / total) * log2(c / total) for c in st.chars.values()) if total else 0.0
        long_labels = mean_label >= s.tunnel_min_mean_label
        high_entropy = entropy >= s.tunnel_min_entropy
        if not (long_labels or high_entropy) or not self.tunnel_cooldown.allow(key, ev.ts):
            return []
        record_ratio = sum(v for k, v in st.qtypes.items() if k in _TUNNEL_TYPES) / st.queries
        confidence = 0.7 + 0.08 * long_labels + 0.08 * high_entropy + 0.07 * (record_ratio >= 0.5)
        confidence = round(min(0.95, confidence), 3)
        duration = max(1.0, st.last - st.start)
        events = list(st.events)
        answered = any(e.response_seen for e in events)
        evidence = [
            Evidence(feature="registered_domain", value=registered),
            Evidence(feature="unique_subdomains", value=len(st.subs), threshold=s.tunnel_min_unique_subdomains,
                     note=f"within {int(duration)} s"),
            Evidence(feature="queries", value=st.queries),
            Evidence(feature="mean_longest_label", value=round(mean_label, 1), threshold=s.tunnel_min_mean_label,
                     unit="chars"),
            Evidence(feature="max_label_length", value=st.max_label, unit="chars"),
            Evidence(feature="subdomain_character_entropy", value=round(entropy, 3), threshold=s.tunnel_min_entropy,
                     unit="bits/char"),
            Evidence(feature="encoded_payload_chars", value=st.total_chars, threshold=s.tunnel_min_payload_chars),
            Evidence(feature="estimated_upstream_rate", value=round(st.total_chars * 5 / 8 / duration, 1),
                     unit="bytes/s", note="assuming base32-style encoding"),
            Evidence(feature="record_types", value={_RECORD_NAMES.get(k, str(k)): v for k, v in st.qtypes.items()}),
            Evidence(feature="tunnel_record_type_ratio", value=round(record_ratio, 3),
                     note="share of TXT, NULL, CNAME and MX queries"),
            Evidence(feature="example_queries", value=st.examples),
        ]
        visibility = Visibility(directions_seen=2.0 if answered else 1.0, sufficient=True,
                                note=None if answered else "only queries were visible")
        scope = EvidenceScope(hosts=[ev.src], ports=[53], proto=17, t0=st.start, t1=ev.ts + 3, max_packets=3000)
        return [make_alert(
            ThreatClass.DNS_TUNNEL, sensor_id=ctx.settings.sensor_id, event_time=ev.ts, window_start=st.start,
            window_end=ev.ts, severity=severity_for(confidence, "high"), confidence=confidence,
            src=ev.src, dst=registered, dport=53,
            flow_ids=sorted({e.community_id for e in events if e.community_id})[:50],
            evidence=evidence, visibility=visibility, detector=self.detector_id,
            custody=custody_for(ctx, [e.ref for e in events], scope), advisory=_TUNNEL_ADVISORY,
        )]

    def _gc(self, now: float) -> None:
        if now - self._last_gc < 60:
            return
        self._last_gc = now
        stale = now - max(self.s.tunnel_window_s, self.s.dga_window_s)
        for key in [k for k, v in self._tunnels.items() if v.last < stale]:
            del self._tunnels[key]
        for src in [k for k, v in self._dga_hits.items() if not v or v[-1][0] < stale]:
            del self._dga_hits[src]
