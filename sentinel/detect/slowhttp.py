"""(a, extended) Slow-HTTP resource exhaustion (Slowloris / slow POST).

Slowloris opens many concurrent connections to one web server and keeps each
one barely alive with a trickle of bytes, never completing a request, to exhaust
the connection pool. From passive metadata this looks like: one source (or a few)
holding many long-lived, established connections to a single (server, port), each
carrying very little payload for its lifetime and rarely closing cleanly.

Detected from flow records only, so it works in both packet and flow-export mode.
"""

from __future__ import annotations

from collections import deque

from sentinel.alerts import Evidence, EvidenceScope, ThreatClass, make_alert, severity_for
from sentinel.config import SlowHttpSettings
from sentinel.detect.base import Context, Cooldown, Detector, custody_for, visibility_of
from sentinel.events import TCP, FlowRecord

_WEB_PORTS = frozenset({80, 443, 8080, 8000, 8443})
_ADVISORY = [
    "Confirm the target web server's connection-pool and worker saturation from production-side monitoring.",
    "Apply per-source connection limits or a reverse-proxy timeout for slow requests at the production edge.",
]


class _Target:
    __slots__ = ("conns", "first", "last")

    def __init__(self, ts: float) -> None:
        self.conns: deque = deque(maxlen=512)  # (src, duration_s, orig_payload, flow)
        self.first = self.last = ts


class SlowHttpDetector(Detector):
    name = "slowhttp"
    version = "1.0"

    def __init__(self, settings: SlowHttpSettings) -> None:
        self.s = settings
        self.cooldown = Cooldown(settings.cooldown_s)
        self._targets: dict[tuple, _Target] = {}
        self._last_gc = 0.0

    def on_flow(self, rec: FlowRecord, ctx: Context) -> list:
        s = self.s
        if not rec.final or rec.proto != TCP or rec.dport not in _WEB_PORTS:
            return []
        # A slow-loris connection is long-lived but moves almost no data and never closes cleanly.
        duration = (rec.last_ts - rec.first_ts)
        if duration < s.min_duration_s:
            return []
        established = rec.orig_payload > 0 or rec.synack
        if not established:
            return []
        key = (rec.dst, rec.dport)
        tgt = self._targets.get(key)
        if tgt is None or rec.last_ts - tgt.last > s.window_s:
            tgt = self._targets[key] = _Target(rec.first_ts)
        tgt.last = rec.last_ts
        slow = rec.orig_payload <= s.max_payload_bytes and rec.state != "closed"
        tgt.conns.append((rec.src, round(duration, 1), rec.orig_payload, slow, rec))
        self._gc(rec.last_ts)

        recent = [c for c in tgt.conns if c[1] >= s.min_duration_s]
        slow_conns = [c for c in recent if c[3]]
        if len(slow_conns) < s.min_connections:
            return []
        sources = {c[0] for c in slow_conns}
        # Concentrated in few sources (a botnet slow-loris still uses far fewer sources than a real user base).
        if len(sources) > s.max_sources:
            return []
        if not self.cooldown.allow(key, rec.last_ts):
            return []

        flows = [c[4] for c in slow_conns][-40:]
        mean_payload = sum(c[2] for c in slow_conns) / len(slow_conns)
        mean_duration = sum(c[1] for c in slow_conns) / len(slow_conns)
        confidence = round(min(0.9, 0.6 + 0.1 * (len(sources) <= 3) + 0.1 * (mean_payload < 200) + 0.1 * (len(slow_conns) >= 2 * s.min_connections)), 3)
        src_label = next(iter(sources)) if len(sources) == 1 else f"multiple ({len(sources)} sources)"
        evidence = [
            Evidence(feature="concurrent_slow_connections", value=len(slow_conns), threshold=s.min_connections,
                     note=f"long-lived, low-payload, unclosed within {int(s.window_s)} s"),
            Evidence(feature="distinct_sources", value=len(sources), threshold=s.max_sources),
            Evidence(feature="mean_connection_duration", value=round(mean_duration, 1), unit="s",
                     threshold=s.min_duration_s),
            Evidence(feature="mean_orig_payload", value=round(mean_payload, 1), unit="bytes",
                     threshold=s.max_payload_bytes, note="bytes the client sent over the whole connection"),
            Evidence(feature="target", value=f"{rec.dst}:{rec.dport}"),
        ]
        scope = EvidenceScope(hosts=sorted(sources | {rec.dst})[:16], ports=[rec.dport], proto=TCP,
                              t0=tgt.first, t1=rec.last_ts, max_packets=3000)
        return [make_alert(
            ThreatClass.SLOW_HTTP, sensor_id=ctx.settings.sensor_id, title="Slow-HTTP resource exhaustion (Slowloris)",
            event_time=rec.last_ts, window_start=tgt.first, window_end=rec.last_ts,
            severity=severity_for(confidence, "high"), confidence=confidence, src=src_label, dst=rec.dst,
            dport=rec.dport, flow_ids=[f.community_id for f in flows], evidence=evidence,
            visibility=visibility_of(flows), detector=self.detector_id,
            custody=custody_for(ctx, [f.first_ref for f in flows], scope), advisory=_ADVISORY,
        )]

    def _gc(self, now: float) -> None:
        if now - self._last_gc < 60:
            return
        self._last_gc = now
        horizon = now - self.s.window_s
        for key in [k for k, v in self._targets.items() if v.last < horizon]:
            del self._targets[key]
