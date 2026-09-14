"""(a) Volumetric and protocol DDoS from per-destination second aggregates.

* SYN flood: SYN rate toward one destination, source cardinality and entropy
  (spoofed floods use many near-uniform sources), handshake completion ratio.
* UDP reflection/amplification: unsolicited large UDP responses from
  amplification service ports, many reflectors, few matching requests.
* UDP flood: raw UDP packet rate above an absolute floor and the destination's
  own learned baseline.

An attack must persist for ``sustain_seconds`` consecutive seconds.
"""

from __future__ import annotations

from collections import Counter, deque

from sentinel.alerts import Evidence, EvidenceScope, ThreatClass, Visibility, make_alert, severity_for
from sentinel.config import DDoSSettings
from sentinel.detect.base import Context, Cooldown, Detector, custody_for, normalised_entropy
from sentinel.events import DstSecond

_ADVISORY = [
    "Raise the incident with the upstream provider or scrubbing service through the out-of-band SOC channel.",
    "Confirm target service health using production-side monitoring (not reachable from this enclave).",
    "Export the evidence bundle before capture rotation.",
]


class DDoSDetector(Detector):
    name = "ddos"
    version = "2.0"

    def __init__(self, settings: DDoSSettings) -> None:
        self.s = settings
        self.cooldown = Cooldown(settings.cooldown_s)
        self._streaks: dict[tuple, deque] = {}
        self._baseline: dict[str, float] = {}

    def on_dst_second(self, st: DstSecond, ctx: Context) -> list:
        s = self.s
        base = self._baseline.get(st.dst)
        mean_amp = st.amp_bytes / st.amp_packets if st.amp_packets else 0.0
        completion = st.synack_sent / st.tcp_syn if st.tcp_syn else 1.0
        unique_sources = len(st.sources)
        entropy = normalised_entropy(st.sources)
        spoofed = unique_sources >= s.min_unique_sources_spoofed and entropy >= s.spoofed_entropy_min

        syn = st.tcp_syn >= s.min_syn_per_s and (completion <= s.max_handshake_completion or spoofed) \
            and (base is None or st.tcp_syn > base * s.baseline_multiplier)
        amp = (st.amp_bytes >= s.min_amp_bytes_per_s and len(st.amp_sources) >= s.min_amp_reflectors
               and mean_amp >= s.min_amp_mean_packet and st.amp_requests_sent < 0.1 * max(1, st.amp_packets))
        # A server answering most datagrams (e.g. a busy resolver) is loaded, not flooded.
        answering = st.udp_sent >= 0.5 * st.udp_packets
        udp = (not amp and not answering and st.udp_packets >= s.min_udp_pps
               and (base is None or st.udp_packets > base * s.baseline_multiplier))

        if not (syn or amp or udp):
            self._baseline[st.dst] = st.packets if base is None else 0.9 * base + 0.1 * st.packets
            if len(self._baseline) > 200_000:
                self._baseline.pop(next(iter(self._baseline)))

        alerts = []
        for kind, active in (("syn", syn), ("amp", amp), ("udp", udp)):
            key = (st.dst, kind)
            streak = self._streaks.get(key)
            if not active:
                if streak is not None:
                    del self._streaks[key]
                continue
            if streak is None or (streak and st.ts - streak[-1].ts > 1):
                streak = self._streaks[key] = deque(maxlen=s.sustain_seconds)
            streak.append(st)
            if len(streak) == s.sustain_seconds and self.cooldown.allow(key, st.ts):
                alerts.append(self._alert(kind, list(streak), base, ctx))
        return alerts

    def _alert(self, kind: str, seconds: list[DstSecond], base: float | None, ctx: Context):
        s = self.s
        dst = seconds[0].dst
        n = len(seconds)
        sources: Counter = Counter()
        truncated = False
        for sec in seconds:
            sources.update(sec.sources)
            truncated = truncated or sec.sources_truncated
        unique_sources = len(sources)
        entropy = normalised_entropy(sources)
        top_source = sources.most_common(1)[0][0] if sources else "unknown"
        src_label = f"multiple ({unique_sources}{'+' if truncated else ''} sources)" if unique_sources > 10 else top_source
        synack = sum(x.synack_sent for x in seconds)
        scope = EvidenceScope(hosts=[dst], t0=float(seconds[0].ts), t1=float(seconds[-1].ts + 1), max_packets=3000)
        evidence: list[Evidence] = []

        if kind == "syn":
            syn_total = sum(x.tcp_syn for x in seconds)
            rate = syn_total / n
            completion = synack / syn_total if syn_total else 0.0
            spoofed = unique_sources >= s.min_unique_sources_spoofed and entropy >= s.spoofed_entropy_min
            threat, title = ThreatClass.SYN_FLOOD, ("Spoofed-source TCP SYN flood" if spoofed else "TCP SYN flood")
            confidence = 0.7 + (0.15 if spoofed else 0.0) + (0.1 if completion <= s.max_handshake_completion else 0.0)
            impact = "critical" if rate >= 5 * s.min_syn_per_s else "high"
            evidence = [
                Evidence(feature="syn_per_second", value=round(rate, 1), threshold=s.min_syn_per_s, unit="packets/s",
                         baseline=round(base, 1) if base is not None else None),
                Evidence(feature="unique_sources", value=unique_sources, threshold=s.min_unique_sources_spoofed,
                         note="source table capped per second" if truncated else None),
                Evidence(feature="source_entropy_normalised", value=round(entropy, 3), threshold=s.spoofed_entropy_min),
                Evidence(feature="handshake_completion_ratio", value=round(completion, 3),
                         threshold=s.max_handshake_completion, note="SYN-ACKs sent by target / SYNs received"),
                Evidence(feature="sustained_seconds", value=n, unit="s"),
            ]
            scope.proto = 6
        elif kind == "amp":
            amp_bytes = sum(x.amp_bytes for x in seconds)
            amp_packets = sum(x.amp_packets for x in seconds)
            reflectors = set().union(*(x.amp_sources for x in seconds))
            requests = sum(x.amp_requests_sent for x in seconds)
            threat, title = ThreatClass.UDP_AMPLIFICATION, "UDP reflection / amplification flood"
            confidence = 0.8 + (0.1 if requests == 0 else 0.0)
            mbps = amp_bytes * 8 / n / 1e6
            impact = "critical" if mbps >= 100 else "high"
            evidence = [
                Evidence(feature="amplified_traffic", value=round(mbps, 2), unit="Mbit/s",
                         threshold=round(s.min_amp_bytes_per_s * 8 / 1e6, 2)),
                Evidence(feature="reflectors", value=len(reflectors), threshold=s.min_amp_reflectors),
                Evidence(feature="mean_response_size", value=round(amp_bytes / max(1, amp_packets), 1), unit="bytes",
                         threshold=s.min_amp_mean_packet),
                Evidence(feature="requests_sent_by_target", value=requests,
                         note="responses without matching requests indicate reflection of spoofed queries"),
                Evidence(feature="sustained_seconds", value=n, unit="s"),
            ]
            src_label = f"multiple ({len(reflectors)} reflectors)"
            scope.proto = 17
        else:
            udp_total = sum(x.udp_packets for x in seconds)
            threat, title = ThreatClass.UDP_FLOOD, "UDP flood"
            confidence = 0.7 + (0.1 if base is not None else 0.0)
            impact = "high"
            evidence = [
                Evidence(feature="udp_packets_per_second", value=round(udp_total / n, 1), unit="packets/s",
                         threshold=s.min_udp_pps, baseline=round(base, 1) if base is not None else None),
                Evidence(feature="udp_packets_sent_by_target_per_second",
                         value=round(sum(x.udp_sent for x in seconds) / n, 1), unit="packets/s",
                         note="well below the received rate: the target is not answering"),
                Evidence(feature="unique_sources", value=unique_sources),
                Evidence(feature="source_entropy_normalised", value=round(entropy, 3)),
                Evidence(feature="sustained_seconds", value=n, unit="s"),
            ]
            scope.proto = 17

        reverse_visible = synack > 0 or any(x.amp_requests_sent for x in seconds)
        visibility = Visibility(
            directions_seen=2.0 if reverse_visible else 1.0,
            handshake_seen=None,
            sufficient=True,
            note=None if reverse_visible else
            "no traffic from the target was observed: it is either overwhelmed or the reverse direction is not tapped; "
            "detection does not depend on it",
        )
        confidence = min(0.97, confidence)
        return make_alert(
            threat, title=title, sensor_id=ctx.settings.sensor_id,
            event_time=float(seconds[-1].ts + 1), window_start=float(seconds[0].ts), window_end=float(seconds[-1].ts + 1),
            severity=severity_for(confidence, impact), confidence=round(confidence, 3),
            src=src_label, dst=dst, evidence=evidence, visibility=visibility, detector=self.detector_id,
            custody=custody_for(ctx, [], scope), advisory=_ADVISORY,
        )
