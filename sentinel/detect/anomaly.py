"""Streaming behavioural anomaly detector (Half-Space Trees).

An online, unsupervised model (Tan, Ting, Liu, IJCAI 2011) that scores how
unusual a flow's numeric feature vector is against the recent stream, with no
labels and bounded memory. It learns continuously from the traffic it sees, so
it needs no training data that would fail to transfer between networks.

Its role is a safety net for behaviour the rule-based detectors do not name
(novel or zero-day patterns). To keep false positives controlled it only raises
an alert when a host's flows are persistently anomalous (a sustained run of
high-scoring windows), and it is a *supporting* signal: the case correlator
does not escalate on an anomaly alone.
"""

from __future__ import annotations

import math
import random
from collections import deque

from sentinel.alerts import Evidence, EvidenceScope, ThreatClass, Visibility, make_alert, severity_for
from sentinel.config import AnomalySettings
from sentinel.detect.base import Context, Cooldown, Detector, custody_for
from sentinel.events import FlowRecord

_FEATURES = (
    "duration_log", "orig_bytes_log", "resp_bytes_log", "orig_pkts_log", "resp_pkts_log",
    "byte_ratio", "mean_orig_pkt", "mean_resp_pkt", "dport_class", "proto_udp", "one_sided",
)


def _feature_vector(rec: FlowRecord) -> list[float]:
    duration = max(0.0, rec.last_ts - rec.first_ts)
    orig_pkts = max(1, rec.orig_pkts)
    resp_pkts = max(1, rec.resp_pkts)
    total = rec.orig_bytes + rec.resp_bytes + 1
    return [
        math.log1p(duration),
        math.log1p(rec.orig_bytes),
        math.log1p(rec.resp_bytes),
        math.log1p(rec.orig_pkts),
        math.log1p(rec.resp_pkts),
        rec.orig_bytes / total,
        rec.orig_bytes / orig_pkts / 1500.0,
        rec.resp_bytes / resp_pkts / 1500.0,
        min(rec.dport, 1024) / 1024.0,
        1.0 if rec.proto == 17 else 0.0,
        1.0 if rec.directions_seen == 1 else 0.0,
    ]


class _Node:
    __slots__ = ("dim", "split", "left", "right", "r_mass", "l_mass", "depth")

    def __init__(self) -> None:
        self.dim = -1
        self.split = 0.0
        self.left = None
        self.right = None
        self.r_mass = 0  # reference-window mass
        self.l_mass = 0  # latest-window mass


class _HalfSpaceTree:
    def __init__(self, dims: int, depth: int, rng: random.Random) -> None:
        self.depth = depth
        low = [rng.random() for _ in range(dims)]
        work = [(l - rng.random(), l + rng.random()) for l in low]  # noqa: E741
        self.root = self._build(0, list(range(dims)), work, rng)

    def _build(self, depth: int, dims: list[int], ranges: list, rng: random.Random) -> _Node:
        node = _Node()
        node.depth = depth
        if depth == self.depth:
            return node
        d = rng.choice(dims)
        lo, hi = ranges[d]
        node.dim = d
        node.split = (lo + hi) / 2.0
        left_ranges = list(ranges)
        right_ranges = list(ranges)
        left_ranges[d] = (lo, node.split)
        right_ranges[d] = (node.split, hi)
        node.left = self._build(depth + 1, dims, left_ranges, rng)
        node.right = self._build(depth + 1, dims, right_ranges, rng)
        return node

    def _leaf_path(self, x: list[float]):
        node = self.root
        nodes = [node]
        while node.dim >= 0:
            node = node.left if x[node.dim] < node.split else node.right
            nodes.append(node)
        return nodes

    def score(self, x: list[float], size_limit: int) -> float:
        node = self.root
        depth = 0
        while node.dim >= 0 and node.r_mass > size_limit:
            node = node.left if x[node.dim] < node.split else node.right
            depth += 1
        return node.r_mass * (2 ** depth)

    def update_latest(self, x: list[float]) -> None:
        for node in self._leaf_path(x):
            node.l_mass += 1

    def commit(self) -> None:
        self._commit(self.root)

    def _commit(self, node: _Node) -> None:
        node.r_mass = node.l_mass
        node.l_mass = 0
        if node.left:
            self._commit(node.left)
            self._commit(node.right)


class HalfSpaceTrees:
    def __init__(self, dims: int, n_trees: int = 25, depth: int = 12, window: int = 250, seed: int = 26145) -> None:
        rng = random.Random(seed)
        self.trees = [_HalfSpaceTree(dims, depth, rng) for _ in range(n_trees)]
        self.window = window
        self.size_limit = max(1, window // 10)
        self.max_score = n_trees * window * (2 ** depth)
        self._count = 0
        self._learned = 0

    def score_and_learn(self, x: list[float]) -> float | None:
        s = sum(t.score(x, self.size_limit) for t in self.trees) if self._learned else None
        for t in self.trees:
            t.update_latest(x)
        self._count += 1
        if self._count >= self.window:
            for t in self.trees:
                t.commit()
            self._count = 0
            self._learned += 1
        if s is None:
            return None
        return 1.0 - min(1.0, s / self.max_score)  # 0 normal .. 1 anomalous


class _HostRun:
    __slots__ = ("high", "seen", "flows", "first", "last", "peak")

    def __init__(self, ts: float) -> None:
        self.high = 0
        self.seen = 0
        self.flows: deque = deque(maxlen=12)
        self.first = self.last = ts
        self.peak = 0.0


class AnomalyDetector(Detector):
    name = "anomaly"
    version = "1.0"

    def __init__(self, settings: AnomalySettings) -> None:
        self.s = settings
        self.model = HalfSpaceTrees(len(_FEATURES), n_trees=settings.n_trees, depth=settings.depth,
                                    window=settings.window)
        self.cooldown = Cooldown(settings.cooldown_s)
        self._hosts: dict[str, _HostRun] = {}
        self._last_gc = 0.0

    def on_flow(self, rec: FlowRecord, ctx: Context) -> list:
        s = self.s
        if not rec.final:
            return []
        host = rec.src if ctx.settings.is_internal(rec.src) or not ctx.settings.is_internal(rec.dst) else rec.dst
        score = self.model.score_and_learn(_feature_vector(rec))
        if score is None:
            return []
        run = self._hosts.get(host)
        if run is None or rec.last_ts - run.last > s.window_s:
            run = self._hosts[host] = _HostRun(rec.first_ts)
        run.seen += 1
        run.last = rec.last_ts
        if score >= s.flow_score_threshold:
            run.high += 1
            run.peak = max(run.peak, score)
            run.flows.append((rec, round(score, 3)))
        self._gc(rec.last_ts)

        if run.high < s.min_anomalous_flows or run.seen < s.min_anomalous_flows:
            return []
        rate = run.high / run.seen
        if rate < s.min_anomalous_fraction or not self.cooldown.allow(host, rec.last_ts):
            return []
        flows = [f for f, _ in run.flows]
        confidence = round(min(0.7, 0.4 + 0.3 * rate), 3)  # capped: this is a supporting signal
        top = sorted(run.flows, key=lambda x: -x[1])[:5]
        evidence = [
            Evidence(feature="anomalous_flows", value=run.high, threshold=s.min_anomalous_flows,
                     note=f"of {run.seen} flows in {int(rec.last_ts - run.first)} s"),
            Evidence(feature="anomalous_fraction", value=round(rate, 3), threshold=s.min_anomalous_fraction),
            Evidence(feature="peak_anomaly_score", value=round(run.peak, 3), threshold=s.flow_score_threshold),
            Evidence(feature="model", value="half-space trees (online, unsupervised)"),
            Evidence(feature="example_flows", value=[f"{f.src}->{f.dst}:{f.dport} score {sc}" for f, sc in top]),
        ]
        scope = EvidenceScope(hosts=[host], t0=run.first, t1=rec.last_ts, max_packets=2000)
        return [make_alert(
            ThreatClass.ANOMALY, sensor_id=ctx.settings.sensor_id,
            title="Persistent behavioural anomaly (unsupervised)", event_time=rec.last_ts,
            window_start=run.first, window_end=rec.last_ts, severity=severity_for(confidence, "medium"),
            confidence=confidence, src=host, dst=flows[-1].dst if flows else host,
            flow_ids=[f.community_id for f in flows], evidence=evidence,
            visibility=Visibility(directions_seen=sum(f.directions_seen for f in flows) / max(1, len(flows)),
                                  sufficient=True, note="supporting signal only; not used alone to open a critical case"),
            detector=self.detector_id, custody=custody_for(ctx, [f.first_ref for f in flows], scope),
            advisory=["Review the host's recent flows for an activity the named detectors did not classify."],
        )]

    def _gc(self, now: float) -> None:
        if now - self._last_gc < 120:
            return
        self._last_gc = now
        horizon = now - self.s.window_s
        for host in [k for k, v in self._hosts.items() if v.last < horizon]:
            del self._hosts[host]
