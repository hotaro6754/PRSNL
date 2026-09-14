"""(e) Reconnaissance and port scanning.

Primary test: Threshold Random Walk (Jung, Paxson, Berger, Balakrishnan 2004), a
sequential hypothesis test over first-contact connection outcomes. A scanner's
connections mostly fail; a benign client's mostly succeed. With the configured
alpha/beta the test bounds its own false-positive and detection rates.

Fallback: fan-out (distinct ports on one host, or distinct hosts on one port).
Outcomes need the reverse direction; when the tap is effectively one-way for
TCP the test is disabled and alerts say so.
"""

from __future__ import annotations

import math
from collections import Counter, deque

from sentinel.alerts import Evidence, EvidenceScope, ThreatClass, make_alert, severity_for
from sentinel.config import ScanSettings
from sentinel.detect.base import Context, Cooldown, Detector, custody_for, visibility_of
from sentinel.events import TCP, FlowRecord

_ADVISORY = [
    "Identify the owner of the scanning host; if internal, treat as possible lateral movement and escalate.",
    "Review exposure of the services that answered (listed in evidence) through the production change process.",
]


class _Source:
    __slots__ = ("llr", "targets", "hosts", "ports", "ports_per_host", "hosts_per_port", "failures", "successes",
                 "first_ts", "last_ts", "flows")

    def __init__(self, ts: float) -> None:
        self.llr = 0.0
        self.targets: set = set()
        self.hosts: set = set()
        self.ports: Counter = Counter()
        self.ports_per_host: dict = {}
        self.hosts_per_port: dict = {}
        self.failures = 0
        self.successes = 0
        self.first_ts = ts
        self.last_ts = ts
        self.flows: deque = deque(maxlen=24)


class ScanDetector(Detector):
    name = "scan"
    version = "2.0"

    def __init__(self, settings: ScanSettings) -> None:
        self.s = settings
        self.cooldown = Cooldown(settings.cooldown_s)
        self._sources: dict[str, _Source] = {}
        self._step_success = math.log(settings.theta1 / settings.theta0)
        self._step_failure = math.log((1 - settings.theta1) / (1 - settings.theta0))
        self._upper = math.log(settings.beta / settings.alpha)
        self._lower = math.log((1 - settings.beta) / (1 - settings.alpha))
        self._recent_two_way: deque = deque(maxlen=2000)
        self._last_gc = 0.0

    def _tcp_reverse_visible(self) -> bool:
        if len(self._recent_two_way) < 200:
            return True  # not enough evidence to judge; assume a normal two-way tap
        return sum(self._recent_two_way) / len(self._recent_two_way) >= 0.3

    def on_flow(self, rec: FlowRecord, ctx: Context) -> list:
        if not rec.final or rec.proto != TCP:
            return []
        if rec.state in ("established", "closed") or rec.synack:
            outcome = True
        elif rec.state in ("attempt", "rejected"):
            outcome = False
        else:
            return []
        if rec.orig_payload:
            # Only data-carrying flows tell us whether the tap copies both directions;
            # bare SYNs (floods, scans) would otherwise look like one-way visibility.
            self._recent_two_way.append(1 if rec.resp_pkts else 0)

        st = self._sources.get(rec.src)
        if st is None or rec.last_ts - st.last_ts > self.s.window_s:
            st = self._sources[rec.src] = _Source(rec.first_ts)
        st.last_ts = rec.last_ts
        target = (rec.dst, rec.dport)
        if target in st.targets:
            return []  # TRW counts first contacts only
        if len(st.targets) < 65536:
            st.targets.add(target)
        st.hosts.add(rec.dst)
        st.ports[rec.dport] += 1
        st.ports_per_host.setdefault(rec.dst, set()).add(rec.dport)
        st.hosts_per_port.setdefault(rec.dport, set()).add(rec.dst)
        st.flows.append(rec)

        if outcome:
            st.successes += 1
        else:
            st.failures += 1
        # A source whose connections received replies demonstrably has its reverse direction visible.
        reverse_visible = st.successes > 0 or self._tcp_reverse_visible()
        if reverse_visible:
            st.llr += self._step_success if outcome else self._step_failure
            if st.llr <= self._lower:
                st.llr = 0.0  # accepted as benign; restart the walk

        self._gc(rec.last_ts)
        return self._evaluate(rec.src, st, reverse_visible, ctx)

    def _evaluate(self, src: str, st: _Source, reverse_visible: bool, ctx: Context) -> list:
        s = self.s
        max_ports_one_host = max((len(v) for v in st.ports_per_host.values()), default=0)
        max_hosts_one_port = max((len(v) for v in st.hosts_per_port.values()), default=0)
        trw = reverse_visible and st.llr >= self._upper and len(st.targets) >= s.min_targets
        fanout = max_ports_one_host >= s.fanout_ports or max_hosts_one_port >= s.fanout_hosts
        failure_ratio = st.failures / max(1, st.failures + st.successes)
        if fanout and reverse_visible and failure_ratio < 0.5:
            fanout = False  # wide but successful fan-out (e.g. crawler, monitoring poller)
        if not (trw or fanout) or not self.cooldown.allow(src, st.last_ts):
            return []

        if max_ports_one_host >= max_hosts_one_port:
            scan_type = "vertical" if len(st.hosts) <= 3 else "mixed"
        else:
            scan_type = "horizontal"
        if trw:
            confidence = 0.9
        elif reverse_visible:
            confidence = 0.75
        else:
            confidence = 0.6
        flows = list(st.flows)
        visibility = visibility_of(flows)
        if not reverse_visible:
            visibility.sufficient = False
            visibility.note = ("TCP responses are mostly not visible on this tap; connection outcomes are unknown, "
                               "so the sequential test is disabled and only fan-out is used")
        duration = max(1e-3, st.last_ts - st.first_ts)
        answered = sorted({(f.dst, f.dport) for f in flows if f.synack})[:10]
        evidence = [
            Evidence(feature="scan_type", value=scan_type),
            Evidence(feature="distinct_targets", value=len(st.targets), threshold=s.min_targets,
                     note="distinct (host, port) first contacts"),
            Evidence(feature="distinct_hosts", value=len(st.hosts), threshold=s.fanout_hosts),
            Evidence(feature="max_ports_on_one_host", value=max_ports_one_host, threshold=s.fanout_ports),
            Evidence(feature="failed_connection_ratio", value=round(failure_ratio, 3)),
            Evidence(feature="trw_log_likelihood_ratio", value=round(st.llr, 2), threshold=round(self._upper, 2),
                     note=f"alpha={s.alpha}, beta={s.beta}"),
            Evidence(feature="probe_rate", value=round(len(st.targets) / duration, 2), unit="targets/s"),
            Evidence(feature="top_ports", value=[p for p, _ in st.ports.most_common(10)]),
            Evidence(feature="services_that_answered", value=[f"{h}:{p}" for h, p in answered]),
        ]
        impact = "high" if ctx.settings.is_internal(src) else "medium"
        scope = EvidenceScope(hosts=[src], proto=TCP, t0=st.first_ts, t1=st.last_ts, max_packets=4000)
        dst_label = next(iter(st.hosts)) if len(st.hosts) == 1 else f"multiple ({len(st.hosts)} hosts)"
        alert = make_alert(
            ThreatClass.SCAN, title=f"{scan_type.capitalize()} port scan", sensor_id=ctx.settings.sensor_id,
            event_time=st.last_ts, window_start=st.first_ts, window_end=st.last_ts,
            severity=severity_for(confidence, impact), confidence=confidence,
            src=src, dst=dst_label, flow_ids=[f.community_id for f in flows][:50], evidence=evidence,
            visibility=visibility, detector=self.detector_id,
            custody=custody_for(ctx, [f.first_ref for f in flows], scope), advisory=_ADVISORY,
        )
        return [alert]

    def _gc(self, now: float) -> None:
        if now - self._last_gc < 60:
            return
        self._last_gc = now
        horizon = now - self.s.window_s
        for src in [k for k, v in self._sources.items() if v.last_ts < horizon]:
            del self._sources[src]
