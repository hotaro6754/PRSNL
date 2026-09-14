import sys
import re

with open('backend/ml/feature_engine.py', 'r') as f:
    content = f.read()

profile_block = '''        # Entity Profiling (Host Baseline)
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
        )'''

new_content = re.sub(r'        # Entity Profiling \(Host Baseline\).*$', profile_block, content, flags=re.DOTALL)

with open('backend/ml/feature_engine.py', 'w') as f:
    f.write(new_content)
