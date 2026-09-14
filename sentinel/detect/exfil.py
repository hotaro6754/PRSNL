"""(f) Data exfiltration: asymmetric outbound volume from an internal host to an
external destination.

Within a window the detector sums outbound and inbound bytes of flow increments
and compares them with the host's own learned outbound baseline (EWMA mean and
variance of past windows). The out/in ratio is only meaningful when both
directions are visible; with one-way visibility the alert is emitted only for
very large volumes, at low confidence, and says why.
"""

from __future__ import annotations

import math
from collections import deque

from sentinel.alerts import Evidence, EvidenceScope, ThreatClass, make_alert, severity_for
from sentinel.config import ExfilSettings
from sentinel.detect.base import Context, Cooldown, Detector, custody_for, scope_for_flows, visibility_of
from sentinel.events import FlowRecord

_ADVISORY = [
    "Determine what data the source host holds and whether this transfer was authorised.",
    "If unauthorised, block the destination at the production egress point and begin incident response.",
]


class _Window:
    __slots__ = ("start", "last", "out", "inn", "flows", "ports", "two_way", "one_way")

    def __init__(self, ts: float) -> None:
        self.start = self.last = ts
        self.out = self.inn = 0
        self.flows: deque = deque(maxlen=20)
        self.ports: set = set()
        self.two_way = self.one_way = 0


class _Baseline:
    __slots__ = ("mean", "var", "windows", "wid", "total")

    def __init__(self, wid: int) -> None:
        self.mean = self.var = 0.0
        self.windows = 0
        self.wid = wid
        self.total = 0


class ExfilDetector(Detector):
    name = "exfil"
    version = "2.0"

    def __init__(self, settings: ExfilSettings) -> None:
        self.s = settings
        self.cooldown = Cooldown(settings.cooldown_s)
        self._windows: dict[tuple, _Window] = {}
        self._baselines: dict[str, _Baseline] = {}
        self._dst_hosts: dict[str, set] = {}

    def _baseline(self, src: str, ts: float, add: int) -> _Baseline:
        wid = int(ts // self.s.window_s)
        b = self._baselines.get(src)
        if b is None:
            b = self._baselines[src] = _Baseline(wid)
        if wid != b.wid:
            alpha = 0.2
            diff = b.total - b.mean
            incr = alpha * diff
            b.mean += incr
            b.var = (1 - alpha) * (b.var + diff * incr)
            b.windows += 1
            b.wid = wid
            b.total = 0
        b.total += add
        return b

    def on_flow(self, rec: FlowRecord, ctx: Context) -> list:
        s = self.s
        if not ctx.settings.is_internal(rec.src) or ctx.settings.is_internal(rec.dst) or rec.dst in s.allow_destinations:
            return []
        hosts = self._dst_hosts.setdefault(rec.dst, set())
        if len(hosts) < 64:
            hosts.add(rec.src)
        baseline = self._baseline(rec.src, rec.last_ts, rec.d_orig_bytes)
        key = (rec.src, rec.dst)
        w = self._windows.get(key)
        if w is None or rec.last_ts - w.start > s.window_s:
            if len(self._windows) > 500_000:
                self._windows.pop(next(iter(self._windows)))
            w = self._windows[key] = _Window(rec.first_ts)
        w.last = rec.last_ts
        w.out += rec.d_orig_bytes
        w.inn += rec.d_resp_bytes
        w.flows.append(rec)
        w.ports.add(rec.dport)
        if rec.directions_seen == 2:
            w.two_way += 1
        else:
            w.one_way += 1

        if w.out < s.min_outbound_bytes:
            return []
        one_sided = w.two_way == 0
        ratio = w.out / max(w.inn, 1)
        if one_sided:
            if w.out < 5 * s.min_outbound_bytes:
                return []
        elif ratio < s.min_ratio:
            return []
        z = None
        if baseline.windows >= 3:
            z = (w.out - baseline.mean) / math.sqrt(baseline.var + (1_000_000.0 ** 2))
            if z < s.baseline_z:
                return []  # this host routinely sends this much
        if not self.cooldown.allow(key, rec.last_ts):
            return []

        flows = list(w.flows)
        visibility = visibility_of(flows, needs_both_directions=True)
        if one_sided:
            confidence = 0.35
        else:
            confidence = 0.6 + 0.15 * (ratio >= 20) + 0.1 * (z is not None) + 0.1 * (len(hosts) <= 1)
        confidence = round(min(0.95, confidence), 3)
        sni = sorted({f.tls.sni for f in flows if f.tls and f.tls.sni})[:5]
        evidence = [
            Evidence(feature="outbound_bytes", value=w.out, threshold=s.min_outbound_bytes, unit="bytes"),
            Evidence(feature="inbound_bytes", value=w.inn if not one_sided else None, unit="bytes",
                     note="reverse direction not visible" if one_sided else None),
            Evidence(feature="outbound_inbound_ratio", value=round(ratio, 1) if not one_sided else None,
                     threshold=s.min_ratio),
            Evidence(feature="window", value=round(w.last - w.start), unit="s"),
            Evidence(feature="outbound_rate", value=round(w.out * 8 / max(1.0, w.last - w.start) / 1e6, 2),
                     unit="Mbit/s"),
            Evidence(feature="destination_ports", value=sorted(w.ports)[:10]),
            Evidence(feature="host_outbound_baseline", value=round(baseline.mean) if baseline.windows else None,
                     unit="bytes/window", note=f"z={z:.1f}" if z is not None else "no baseline yet for this host"),
            Evidence(feature="internal_hosts_contacting_destination", value=len(hosts)),
        ]
        if sni:
            evidence.append(Evidence(feature="tls_sni", value=sni))
        return [make_alert(
            ThreatClass.EXFILTRATION, sensor_id=ctx.settings.sensor_id, event_time=rec.last_ts,
            window_start=w.start, window_end=w.last, severity=severity_for(confidence, "high"),
            confidence=confidence, src=rec.src, dst=rec.dst, dport=rec.dport,
            flow_ids=[f.community_id for f in flows], evidence=evidence, visibility=visibility,
            detector=self.detector_id,
            custody=custody_for(ctx, [f.first_ref for f in flows], scope_for_flows(flows, [rec.src, rec.dst], 400)),
            advisory=_ADVISORY,
        )]
