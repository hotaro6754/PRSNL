"""(b) Botnet C2 beaconing: connections that repeat at regular intervals.

Per (internal source, external destination, port, protocol) the detector keeps
connection start times and request sizes and scores how regular they are:

* timing: Bowley skewness and median absolute deviation (MAD) of intervals,
  which tolerate jitter and outliers far better than a coefficient of variation
* size: the same two measures over request bytes (implants send near-constant check-ins)
* persistence: number of observed intervals

Many internal hosts polling the same destination on a schedule is typical of
update/telemetry services; such alerts are kept but downgraded.
"""

from __future__ import annotations

import ipaddress
import statistics
from collections import deque

from sentinel.alerts import Evidence, EvidenceScope, ThreatClass, make_alert, severity_for
from sentinel.config import BeaconSettings
from sentinel.detect.base import Context, Cooldown, Detector, custody_for, visibility_of
from sentinel.events import FlowRecord

_ADVISORY = [
    "Identify the process on the source host making these connections (EDR / host forensics outside the enclave).",
    "Check the destination and TLS fingerprint against threat intelligence brought into the enclave offline.",
]
_POPULAR_DESTINATION_HOSTS = 5


def bowley_skew(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
    if q3 == q1 or q2 == q1 or q2 == q3:
        return 0.0
    return (q3 + q1 - 2 * q2) / (q3 - q1)


def dispersion(values: list[float]) -> tuple[float, float]:
    median = statistics.median(values)
    mad = statistics.median(abs(v - median) for v in values)
    return median, mad


class _Stream:
    __slots__ = ("starts", "sizes", "flows", "first_ts", "last_ts")

    def __init__(self, maxlen: int, ts: float) -> None:
        self.starts: deque = deque(maxlen=maxlen)
        self.sizes: deque = deque(maxlen=maxlen)
        self.flows: deque = deque(maxlen=16)
        self.first_ts = ts
        self.last_ts = ts


class BeaconDetector(Detector):
    name = "beacon"
    version = "2.0"

    def __init__(self, settings: BeaconSettings) -> None:
        self.s = settings
        self.cooldown = Cooldown(settings.cooldown_s)
        self._streams: dict[tuple, _Stream] = {}
        self._dst_hosts: dict[str, set] = {}
        self._last_gc = 0.0

    def score(self, stream: _Stream) -> dict | None:
        starts = sorted(stream.starts)
        intervals = [b - a for a, b in zip(starts, starts[1:]) if b - a > 0.001]
        if len(intervals) < self.s.min_connections - 1:
            return None
        median, mad = dispersion(intervals)
        if median < self.s.min_median_interval_s:
            return None
        sizes = [float(x) for x in stream.sizes]
        size_median, size_mad = dispersion(sizes)
        time_skew = bowley_skew(intervals)
        size_skew = bowley_skew(sizes)
        size_dispersion = size_mad / size_median if size_median else 0.0
        score = (
            0.35 * (1 - min(1.0, abs(time_skew)))
            + 0.35 * (1 - min(1.0, mad / median))
            + 0.10 * min(1.0, len(intervals) / (2 * self.s.min_connections))
            + 0.10 * (1 - min(1.0, abs(size_skew)))
            + 0.10 * (1 - min(1.0, size_dispersion))
        )
        return {"score": score, "median": median, "mad": mad, "time_skew": time_skew, "size_median": size_median,
                "size_dispersion": size_dispersion, "intervals": len(intervals), "span": starts[-1] - starts[0]}

    def on_flow(self, rec: FlowRecord, ctx: Context) -> list:
        s = self.s
        if not rec.first_export or rec.dport in s.ignore_ports:
            return []
        if not ctx.settings.is_internal(rec.src) or ctx.settings.is_internal(rec.dst):
            return []
        hosts = self._dst_hosts.setdefault(rec.dst, set())
        if len(hosts) < 64:
            hosts.add(rec.src)
        key = (rec.src, rec.dst, rec.dport, rec.proto)
        stream = self._streams.get(key)
        if stream is None:
            stream = self._streams[key] = _Stream(s.max_history, rec.first_ts)
        stream.starts.append(rec.first_ts)
        stream.sizes.append(rec.orig_payload)
        stream.flows.append(rec)
        stream.last_ts = rec.first_ts
        self._gc(rec.first_ts)
        if len(stream.starts) < s.min_connections:
            return []
        result = self.score(stream)
        if result is None or result["score"] < s.score_threshold or not self.cooldown.allow(key, rec.first_ts):
            return []
        return [self._alert(rec, stream, result, len(hosts), ctx)]

    def _alert(self, rec: FlowRecord, stream: _Stream, r: dict, dst_hosts: int, ctx: Context):
        s = self.s
        confidence = 0.6 + (r["score"] - s.score_threshold) / (1 - s.score_threshold) * 0.35
        impact = "high"
        note = None
        if dst_hosts >= _POPULAR_DESTINATION_HOSTS:
            confidence *= 0.6
            impact = "low"
            note = f"{dst_hosts} internal hosts poll this destination on a schedule (typical of update or telemetry services)"
        flows = list(stream.flows)
        tls = next((f.tls for f in reversed(flows) if f.tls), None)
        sni = tls.sni if tls else None
        try:
            ipaddress.ip_address(sni or "")
            sni_is_ip = True
        except ValueError:
            sni_is_ip = False
        evidence = [
            Evidence(feature="connections_observed", value=r["intervals"] + 1, threshold=s.min_connections),
            Evidence(feature="median_interval", value=round(r["median"], 2), unit="s"),
            Evidence(feature="interval_mad", value=round(r["mad"], 2), unit="s"),
            Evidence(feature="jitter", value=round(100 * r["mad"] / r["median"], 1), unit="%"),
            Evidence(feature="interval_bowley_skew", value=round(r["time_skew"], 3)),
            Evidence(feature="median_request_payload", value=round(r["size_median"]), unit="bytes"),
            Evidence(feature="request_size_dispersion", value=round(r["size_dispersion"], 3)),
            Evidence(feature="beacon_score", value=round(r["score"], 3), threshold=s.score_threshold),
            Evidence(feature="observed_span", value=round(r["span"]), unit="s"),
            Evidence(feature="internal_hosts_contacting_destination", value=dst_hosts, note=note),
        ]
        if tls:
            evidence.append(Evidence(feature="tls_sni", value=sni, note="SNI is an IP literal" if sni_is_ip else None))
            evidence.append(Evidence(feature="tls_ja4", value=tls.ja4))
        scope = EvidenceScope(hosts=[rec.src, rec.dst], ports=[rec.dport], proto=rec.proto,
                              t0=stream.starts[0], t1=rec.last_ts, max_packets=2000)
        confidence = round(min(0.95, confidence), 3)
        return make_alert(
            ThreatClass.BEACONING, sensor_id=ctx.settings.sensor_id,
            title="Periodic C2 beaconing" + (" over TLS" if tls else ""),
            event_time=rec.first_ts, window_start=stream.starts[0], window_end=rec.last_ts,
            severity=severity_for(confidence, impact), confidence=confidence,
            src=rec.src, dst=rec.dst, dport=rec.dport, flow_ids=[f.community_id for f in flows],
            evidence=evidence, visibility=visibility_of(flows), detector=self.detector_id,
            custody=custody_for(ctx, [f.first_ref for f in flows], scope), advisory=_ADVISORY,
        )

    def _gc(self, now: float) -> None:
        if now - self._last_gc < 300:
            return
        self._last_gc = now
        horizon = now - self.s.ttl_s
        for key in [k for k, v in self._streams.items() if v.last_ts < horizon]:
            del self._streams[key]
