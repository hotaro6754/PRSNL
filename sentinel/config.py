"""Runtime settings. Every threshold a detector uses lives here so it can be
tuned, documented and reported alongside results."""

from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass, field


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value not in (None, "") else default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


DEFAULT_INTERNAL_NETS = ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7")

# UDP services abused for reflection/amplification (source port of the reflected traffic).
AMPLIFICATION_PORTS = frozenset({17, 19, 53, 69, 111, 123, 137, 161, 389, 1900, 3702, 5353, 11211})


@dataclass(slots=True)
class FlowSettings:
    tcp_idle_s: float = 60.0
    tcp_attempt_s: float = 5.0  # SYN seen, no reply: exported as a failed attempt after this
    tcp_closed_linger_s: float = 2.0
    udp_idle_s: float = 30.0
    active_timeout_s: float = 60.0  # long flows are exported incrementally
    splt_packets: int = 20
    tls_buffer_bytes: int = 16384
    dns_response_wait_s: float = 3.0
    dst_stats_min_packets: int = 20  # per-destination second aggregates below this are not emitted


@dataclass(slots=True)
class DDoSSettings:
    min_syn_per_s: float = 400.0
    min_unique_sources_spoofed: int = 200
    spoofed_entropy_min: float = 0.85  # normalised source entropy
    max_handshake_completion: float = 0.2
    min_amp_bytes_per_s: float = 500_000.0  # 4 Mbit/s; reflector count and unsolicited-response checks keep it specific
    min_amp_reflectors: int = 30
    min_amp_mean_packet: float = 300.0
    min_udp_pps: float = 3000.0
    baseline_multiplier: float = 8.0
    sustain_seconds: int = 3
    cooldown_s: float = 120.0


@dataclass(slots=True)
class ScanSettings:
    theta0: float = 0.8  # P(connection succeeds | benign)
    theta1: float = 0.2  # P(connection succeeds | scanner)
    alpha: float = 0.01  # target false-positive rate of the sequential test
    beta: float = 0.99  # target detection rate
    min_targets: int = 10
    fanout_ports: int = 50
    fanout_hosts: int = 50
    window_s: float = 300.0
    cooldown_s: float = 600.0


@dataclass(slots=True)
class BeaconSettings:
    min_connections: int = 8
    max_history: int = 96
    min_median_interval_s: float = 5.0
    score_threshold: float = 0.80
    ignore_ports: frozenset = frozenset({53, 123, 5353})
    ttl_s: float = 86400.0
    cooldown_s: float = 3600.0


@dataclass(slots=True)
class DnsSettings:
    dga_probability: float = 0.90
    dga_min_domains: int = 6
    dga_window_s: float = 600.0
    tunnel_window_s: float = 120.0
    tunnel_min_unique_subdomains: int = 40
    tunnel_min_mean_label: float = 18.0
    tunnel_min_payload_chars: int = 2500
    tunnel_min_entropy: float = 3.3
    popular_domain_hosts: int = 15  # a domain queried by this many internal hosts is treated as a service
    cooldown_s: float = 900.0


@dataclass(slots=True)
class TlsSettings:
    rare_fingerprint_max_hosts: int = 2
    min_repeat_sessions: int = 5
    cooldown_s: float = 3600.0


@dataclass(slots=True)
class ExfilSettings:
    window_s: float = 600.0
    min_outbound_bytes: int = 20_000_000
    min_ratio: float = 8.0
    baseline_z: float = 4.0
    cooldown_s: float = 1800.0
    allow_destinations: tuple = ()  # sanctioned upload targets (e.g. off-site backup), set per deployment


@dataclass(slots=True)
class SlowHttpSettings:
    min_connections: int = 30       # concurrent slow connections to one target
    max_sources: int = 8            # slow-loris comes from few sources, not a real user base
    min_duration_s: float = 20.0    # a slow connection is held open far longer than a normal request
    max_payload_bytes: int = 2000   # total bytes the client sent over the whole connection
    window_s: float = 120.0
    cooldown_s: float = 600.0


@dataclass(slots=True)
class AnomalySettings:
    n_trees: int = 25
    depth: int = 12
    window: int = 250              # flows per learning window
    flow_score_threshold: float = 0.88
    min_anomalous_flows: int = 20
    min_anomalous_fraction: float = 0.7
    window_s: float = 600.0
    cooldown_s: float = 1800.0
    enabled: bool = True


@dataclass(slots=True)
class ArchiveSettings:
    enabled: bool = True
    max_flows_per_source: int = 5_000_000   # bound the per-source flow archive


@dataclass(slots=True)
class Settings:
    internal_nets: tuple = DEFAULT_INTERNAL_NETS
    flow: FlowSettings = field(default_factory=FlowSettings)
    ddos: DDoSSettings = field(default_factory=DDoSSettings)
    scan: ScanSettings = field(default_factory=ScanSettings)
    beacon: BeaconSettings = field(default_factory=BeaconSettings)
    dns: DnsSettings = field(default_factory=DnsSettings)
    tls: TlsSettings = field(default_factory=TlsSettings)
    exfil: ExfilSettings = field(default_factory=ExfilSettings)
    slowhttp: SlowHttpSettings = field(default_factory=SlowHttpSettings)
    anomaly: AnomalySettings = field(default_factory=AnomalySettings)
    archive: ArchiveSettings = field(default_factory=ArchiveSettings)
    data_dir: str = "var"
    sensor_id: str = "sentinel-01"
    _nets: list = field(default_factory=list, init=False, repr=False)
    _internal_cache: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        self._nets = [ipaddress.ip_network(n) for n in self.internal_nets]

    def is_internal(self, ip: str) -> bool:
        cache = self._internal_cache
        hit = cache.get(ip)
        if hit is not None:
            return hit
        try:
            addr = ipaddress.ip_address(ip)
            result = any(addr in net for net in self._nets)
        except ValueError:
            result = False
        if len(cache) >= 500_000:
            cache.clear()
        cache[ip] = result
        return result

    @classmethod
    def from_env(cls) -> "Settings":
        nets = os.getenv("SENTINEL_INTERNAL_NETS")
        settings = cls(
            internal_nets=tuple(n.strip() for n in nets.split(",")) if nets else DEFAULT_INTERNAL_NETS,
            data_dir=os.getenv("SENTINEL_DATA_DIR", "var"),
            sensor_id=os.getenv("SENTINEL_SENSOR_ID", "sentinel-01"),
        )
        settings.exfil.min_outbound_bytes = _env_int("SENTINEL_EXFIL_MIN_BYTES", settings.exfil.min_outbound_bytes)
        settings.ddos.min_syn_per_s = _env_float("SENTINEL_DDOS_MIN_SYN", settings.ddos.min_syn_per_s)
        allow = os.getenv("SENTINEL_ALLOW_DESTINATIONS")
        if allow:
            settings.exfil.allow_destinations = tuple(x.strip() for x in allow.split(",") if x.strip())
        return settings
