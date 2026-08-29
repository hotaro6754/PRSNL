import time
import math
import numpy as np
from typing import List, Optional
from backend.contracts.observation import NetworkObservation
from backend.contracts.features import FeatureVector
from backend.ml.host_profile import HostBehaviorManager

class TumblingWindowFeatureEngine:
    def __init__(self, window_size_ms: int = 10000, host_manager=None):
        self.window_size_ms = window_size_ms
        self.host_manager = host_manager or HostBehaviorManager()

    def extract_features(self, flows: List[NetworkObservation]) -> Optional[FeatureVector]:
        if not flows:
            return None

        flows_sorted = sorted(flows, key=lambda x: x.timestamp)
        first_ts = flows_sorted[0].timestamp
        last_ts = flows_sorted[-1].timestamp
        duration_s = max(1.0, (last_ts - first_ts) / 1000.0)

        packet_count = 0
        byte_count = 0
        src_packet_count = 0
        dst_packet_count = 0
        src_byte_count = 0
        dst_byte_count = 0
        syn_count = 0
        fin_count = 0
        rst_count = 0
        udp_count = 0
        tcp_count = 0
        icmp_count = 0

        unique_src_ips = set()
        unique_dst_ips = set()
        unique_ports = set()
        dns_queries = []
        tls_snis = []

        packet_sizes = []
        iats = []

        for obs in flows_sorted:
            packet_count += obs.packets
            byte_count += obs.bidirectional_bytes
            src_packet_count += obs.orig_packets
            dst_packet_count += obs.resp_packets
            src_byte_count += obs.orig_ip_bytes
            dst_byte_count += obs.resp_ip_bytes
            
            unique_src_ips.add(obs.source_ip)
            unique_dst_ips.add(obs.destination_ip)
            unique_ports.add(obs.destination_port)
            
            if obs.tcp_syn_orig: syn_count += 1
            if obs.tcp_syn_resp: syn_count += 1
            if obs.tcp_fin_orig: fin_count += 1
            if obs.tcp_fin_resp: fin_count += 1
            if obs.tcp_rst_orig: rst_count += 1
            if obs.tcp_rst_resp: rst_count += 1
            
            if obs.protocol == 17: udp_count += 1
            elif obs.protocol == 6: tcp_count += 1
            elif obs.protocol == 1: icmp_count += 1
            
            if obs.dns_query: dns_queries.append(obs.dns_query)
            if obs.tls_sni: tls_snis.append(obs.tls_sni)
            
            if obs.packets > 0:
                packet_sizes.append(obs.bidirectional_bytes / obs.packets)
            iats.append(obs.timestamp)

        # Basic Stats
        import numpy as np
        import math
        
        size_mean = float(np.mean(packet_sizes)) if packet_sizes else 0.0
        size_std = float(np.std(packet_sizes)) if packet_sizes else 0.0
        size_min = float(np.min(packet_sizes)) if packet_sizes else 0.0
        size_max = float(np.max(packet_sizes)) if packet_sizes else 0.0

        if len(iats) > 1:
            diffs = np.diff(iats)
            iat_mean = float(np.mean(diffs))
            iat_std = float(np.std(diffs))
            iat_cv = float(iat_std / iat_mean) if iat_mean > 0 else 0.0
        else:
            iat_mean = 0.0
            iat_std = 0.0
            iat_cv = 0.0

        packet_rate = float(packet_count) / duration_s
        byte_rate = float(byte_count) / duration_s

        syn_ratio = float(syn_count) / max(1, tcp_count)
        fin_ratio = float(fin_count) / max(1, tcp_count)
        rst_ratio = float(rst_count) / max(1, tcp_count)
        udp_ratio = float(udp_count) / max(1, len(flows_sorted))
        tcp_ratio = float(tcp_count) / max(1, len(flows_sorted))
        icmp_ratio = float(icmp_count) / max(1, len(flows_sorted))

        directionality = 0.0
        if packet_count > 0:
            directionality = float(src_packet_count - dst_packet_count) / float(packet_count)

        fan_in = len(unique_src_ips)
        fan_out = len(unique_dst_ips)

        def shannon(string):
            if not string: return 0.0
            probs = [string.count(c) / len(string) for c in set(string)]
            return -sum(p * math.log(p, 2) for p in probs)

        dns_ent = sum(shannon(q) for q in dns_queries) / max(1, len(dns_queries))
        tls_ent = sum(shannon(s) for s in tls_snis) / max(1, len(tls_snis))
        
        # Entity Profiling (Host Baseline)
        host_ip = flows_sorted[0].source_ip
        if self.host_manager:
            profile = self.host_manager.get_features(host_ip, last_ts)
        else:
            profile = {}

        return FeatureVector(
            window_duration=duration_s,
            packet_count=packet_count,
            byte_count=byte_count,
            src_packet_count=src_packet_count,
            dst_packet_count=dst_packet_count,
            src_byte_count=src_byte_count,
            dst_byte_count=dst_byte_count,
            packet_size_mean=size_mean,
            packet_size_std=size_std,
            packet_size_min=size_min,
            packet_size_max=size_max,
            iat_mean=iat_mean,
            iat_std=iat_std,
            iat_cv=iat_cv,
            packet_rate=packet_rate,
            byte_rate=byte_rate,
            syn_ratio=syn_ratio,
            fin_ratio=fin_ratio,
            rst_ratio=rst_ratio,
            udp_ratio=udp_ratio,
            tcp_ratio=tcp_ratio,
            icmp_ratio=icmp_ratio,
            directionality=directionality,
            fan_in=fan_in,
            fan_out=fan_out,
            dns_entropy=dns_ent,
            tls_sni_entropy=tls_ent,
            
            host_connections_5m=profile.get('connections_5m', 0),
            host_unique_dests_5m=profile.get('unique_dests_5m', 0),
            host_unique_ports_5m=profile.get('unique_ports_5m', 0),
            host_dns_queries_5m=profile.get('dns_queries_5m', 0),
            host_tls_connections_5m=profile.get('tls_connections_5m', 0),
            host_bytes_out_5m=profile.get('bytes_out_5m', 0),
            host_bytes_in_5m=profile.get('bytes_in_5m', 0),
            
            host_connections_1h=profile.get('connections_1h', 0),
            host_unique_dests_1h=profile.get('unique_dests_1h', 0),
            host_unique_ports_1h=profile.get('unique_ports_1h', 0),
            host_dns_queries_1h=profile.get('dns_queries_1h', 0),
            host_tls_connections_1h=profile.get('tls_connections_1h', 0),
            host_bytes_out_1h=profile.get('bytes_out_1h', 0),
            host_bytes_in_1h=profile.get('bytes_in_1h', 0),
            
            host_connections_24h=profile.get('connections_24h', 0),
            host_unique_dests_24h=profile.get('unique_dests_24h', 0),
            host_unique_ports_24h=profile.get('unique_ports_24h', 0),
            host_dns_queries_24h=profile.get('dns_queries_24h', 0),
            host_tls_connections_24h=profile.get('tls_connections_24h', 0),
            host_bytes_out_24h=profile.get('bytes_out_24h', 0),
            host_bytes_in_24h=profile.get('bytes_in_24h', 0)
        )
FEATURE_COLUMNS = ['window_duration', 'packet_count', 'byte_count', 'src_packet_count', 'dst_packet_count', 'src_byte_count', 'dst_byte_count', 'packet_size_mean', 'packet_size_std', 'packet_size_min', 'packet_size_max', 'iat_mean', 'iat_std', 'iat_cv', 'packet_rate', 'byte_rate', 'syn_ratio', 'fin_ratio', 'rst_ratio', 'udp_ratio', 'tcp_ratio', 'icmp_ratio', 'directionality', 'fan_in', 'fan_out', 'dns_entropy', 'tls_sni_entropy', 'host_connections_5m', 'host_unique_dests_5m', 'host_unique_ports_5m', 'host_dns_queries_5m', 'host_tls_connections_5m', 'host_bytes_out_5m', 'host_bytes_in_5m', 'host_connections_1h', 'host_unique_dests_1h', 'host_unique_ports_1h', 'host_dns_queries_1h', 'host_tls_connections_1h', 'host_bytes_out_1h', 'host_bytes_in_1h', 'host_connections_24h', 'host_unique_dests_24h', 'host_unique_ports_24h', 'host_dns_queries_24h', 'host_tls_connections_24h', 'host_bytes_out_24h', 'host_bytes_in_24h']
