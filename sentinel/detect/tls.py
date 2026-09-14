"""(d) Malware inside encrypted sessions, from handshake metadata only.

1. Known-bad client fingerprint: JA3 match against an offline blocklist
   (abuse.ch SSLBL snapshot; the list is historical, so matches are evidence).
2. Suspicious session: a client fingerprint (JA4) that almost no other internal
   host uses, repeatedly connecting to a destination with no SNI, an IP-literal
   SNI, or a registered domain outside the popular-domain list. Commodity
   implants use their own TLS stacks and rarely browse like people do.

Periodicity of the same sessions is scored by the beacon detector; the case
correlator escalates when both fire for one host.
"""

from __future__ import annotations

import ipaddress
from collections import deque

import statistics

from sentinel.alerts import Evidence, EvidenceScope, ThreatClass, Visibility, make_alert, severity_for
from sentinel.config import TlsSettings
from sentinel.detect.base import Context, Cooldown, Detector, custody_for
from sentinel.detect.dns import split_name
from sentinel.events import FlowRecord, TlsEvent
from sentinel.intel.toplist import TopList

_ADVISORY = [
    "Correlate the client fingerprint with software inventory for the source host.",
    "Investigate the destination with offline threat intelligence; do not contact it from the enclave.",
]
_WARMUP_TLS_HOSTS = 20


class _Session:
    __slots__ = ("count", "first", "last", "events")

    def __init__(self, ts: float) -> None:
        self.count = 0
        self.first = self.last = ts
        self.events: deque = deque(maxlen=16)


class TlsDetector(Detector):
    name = "tls"
    version = "2.0"

    def __init__(self, settings: TlsSettings, toplist: TopList | None, ja3_blocklist: dict[str, str]) -> None:
        self.s = settings
        self.toplist = toplist or TopList({}, "none")
        self.blocklist = ja3_blocklist
        self.cooldown = Cooldown(settings.cooldown_s)
        self._sessions: dict[tuple, _Session] = {}
        self._tls_hosts: set = set()
        self._splt: dict[tuple, list] = {}  # (src,dst,dport) -> most recent completed flow's SPLT

    def on_flow(self, rec: FlowRecord, ctx: Context) -> list:
        # Cache the packet-size / inter-arrival sequence (SPLT) of completed encrypted
        # flows, so a suspicious-session alert can carry the "packet-size and timing
        # sequence" evidence the problem statement asks for (payload never inspected).
        if rec.final and rec.splt and (rec.dport in (443, 8443, 853) or rec.tls is not None):
            self._splt[(rec.src, rec.dst, rec.dport)] = rec.splt
            if len(self._splt) > 200_000:
                self._splt.pop(next(iter(self._splt)))
        return []

    def _splt_evidence(self, key: tuple) -> list:
        splt = self._splt.get(key)
        if not splt:
            return []
        sizes = [abs(s) for s, _ in splt]
        iats = [t for _, t in splt[1:]]
        directions = "".join("c" if s >= 0 else "s" for s, _ in splt)  # client / server order
        size_cv = round(statistics.pstdev(sizes) / statistics.mean(sizes), 3) if len(sizes) > 1 and statistics.mean(sizes) else 0.0
        iat_cv = round(statistics.pstdev(iats) / statistics.mean(iats), 3) if len(iats) > 1 and statistics.mean(iats) else 0.0
        return [
            Evidence(feature="splt_packet_sizes", value=sizes[:12], unit="bytes",
                     note="first payload sizes (signed by direction); no payload content inspected"),
            Evidence(feature="splt_direction_sequence", value=directions[:16]),
            Evidence(feature="splt_size_cv", value=size_cv, note="low variance is typical of automated C2"),
            Evidence(feature="splt_interarrival_cv", value=iat_cv, unit="ratio"),
        ]

    def on_tls(self, ev: TlsEvent, ctx: Context) -> list:
        info = ev.tls
        alerts = []
        if len(self._tls_hosts) < 100_000:
            self._tls_hosts.add(ev.src)
        fingerprint_hosts = ctx.note_ja4(info.ja4, ev.src) if info.ja4 else 0

        reason = self.blocklist.get(info.ja3 or "")
        if reason and self.cooldown.allow(("ja3", ev.src, info.ja3), ev.ts):
            confidence = 0.6
            alerts.append(make_alert(
                ThreatClass.TLS_KNOWN_BAD, sensor_id=ctx.settings.sensor_id, event_time=ev.ts, window_start=ev.ts,
                window_end=ev.ts, severity=severity_for(confidence, "high"), confidence=confidence,
                src=ev.src, dst=ev.dst, dport=ev.dport, flow_ids=[ev.community_id],
                evidence=[
                    Evidence(feature="tls_ja3", value=info.ja3, note=f"listed by abuse.ch SSLBL as {reason}"),
                    Evidence(feature="tls_ja4", value=info.ja4),
                    Evidence(feature="tls_sni", value=info.sni),
                    Evidence(feature="intel_age", value="SSLBL JA3 list last updated 2021-08-03",
                             note="fingerprints can be shared by benign software; corroborate before acting"),
                ],
                visibility=Visibility(directions_seen=1.0, sufficient=True), detector=self.detector_id,
                custody=custody_for(ctx, [ev.ref],
                                    EvidenceScope(hosts=[ev.src, ev.dst], ports=[ev.dport], proto=6, t0=ev.ts - 1,
                                                  t1=ev.ts + 5, max_packets=200)),
                advisory=_ADVISORY,
            ))

        key = (ev.src, ev.dst, ev.dport)
        session = self._sessions.get(key)
        if session is None:
            if len(self._sessions) > 500_000:
                self._sessions.pop(next(iter(self._sessions)))
            session = self._sessions[key] = _Session(ev.ts)
        session.count += 1
        session.last = ev.ts
        session.events.append(ev)

        if (session.count < self.s.min_repeat_sessions or len(self._tls_hosts) < _WARMUP_TLS_HOSTS
                or not info.ja4 or not ctx.settings.is_internal(ev.src) or ctx.settings.is_internal(ev.dst)):
            return alerts
        rare = fingerprint_hosts <= self.s.rare_fingerprint_max_hosts
        sni = info.sni
        try:
            ipaddress.ip_address(sni or "")
            sni_ip = True
        except ValueError:
            sni_ip = False
        missing_sni = sni is None or sni_ip
        registered = split_name(sni)[2] if sni and not sni_ip else ""
        unranked = bool(registered) and self.toplist.rank(registered) is None
        old_version = info.version in ("TLS1.0", "TLS1.1", "SSL3.0")
        if not (rare and (missing_sni or unranked)) or not self.cooldown.allow(("session",) + key, ev.ts):
            return alerts

        indicators = [name for name, hit in (("no_or_ip_sni", missing_sni), ("unranked_domain", unranked),
                                              ("legacy_tls_version", old_version)) if hit]
        confidence = round(min(0.9, 0.55 + 0.1 * len(indicators)), 3)
        events = list(session.events)
        alerts.append(make_alert(
            ThreatClass.TLS_SUSPICIOUS, sensor_id=ctx.settings.sensor_id, event_time=ev.ts,
            window_start=session.first, window_end=ev.ts, severity=severity_for(confidence, "high"),
            confidence=confidence, src=ev.src, dst=ev.dst, dport=ev.dport,
            flow_ids=[e.community_id for e in events if e.community_id],
            evidence=[
                Evidence(feature="tls_ja4", value=info.ja4),
                Evidence(feature="tls_ja3", value=info.ja3),
                Evidence(feature="internal_hosts_using_fingerprint", value=fingerprint_hosts,
                         threshold=self.s.rare_fingerprint_max_hosts,
                         note=f"out of {len(self._tls_hosts)} hosts seen using TLS"),
                Evidence(feature="tls_sni", value=sni, note="IP literal" if sni_ip else None),
                Evidence(feature="sni_registered_domain_rank", value=None if not registered else self.toplist.rank(registered),
                         note="not in popular-domain list" if unranked else None),
                Evidence(feature="alpn", value=info.alpn),
                Evidence(feature="offered_tls_version", value=info.version),
                Evidence(feature="sessions_to_destination", value=session.count, threshold=self.s.min_repeat_sessions),
                Evidence(feature="indicators", value=indicators),
                *self._splt_evidence(key),
            ],
            visibility=Visibility(directions_seen=1.0, sufficient=True,
                                  note="decision uses the client handshake only; payload is never inspected"),
            detector=self.detector_id,
            custody=custody_for(ctx, [e.ref for e in events],
                                EvidenceScope(hosts=[ev.src, ev.dst], ports=[ev.dport], proto=6, t0=session.first,
                                              t1=ev.ts + 5, max_packets=1500)),
            advisory=_ADVISORY,
        ))
        return alerts
