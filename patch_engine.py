import re

with open('backend/ml/feature_engine.py', 'r') as f:
    content = f.read()

# Update packet/byte accumulation
new_acc = '''        for flow in flows:
            packet_count += flow.packets
            byte_count += flow.bidirectional_bytes
            src_packet_count += flow.orig_packets
            dst_packet_count += flow.resp_packets
            src_byte_count += flow.orig_ip_bytes
            dst_byte_count += flow.resp_ip_bytes
            
            unique_src_ips.add(flow.source_ip)
            unique_dst_ips.add(flow.destination_ip)
            
            if flow.tcp_syn_orig: syn_count += 1
            if flow.tcp_syn_resp: syn_count += 1
            if flow.tcp_fin_orig: fin_count += 1
            if flow.tcp_fin_resp: fin_count += 1
            if flow.tcp_rst_orig: rst_count += 1
            if flow.tcp_rst_resp: rst_count += 1
            
            if flow.protocol == 17: udp_count += 1
            elif flow.protocol == 6: tcp_count += 1
            elif flow.protocol == 1: icmp_count += 1
            
            if flow.dns_query: dns_queries.append(flow.dns_query)
            if flow.tls_sni: tls_snis.append(flow.tls_sni)
            
            # Using IP bytes for packet size approximation (average per flow)
            if flow.packets > 0:
                packet_sizes.append(flow.bidirectional_bytes / flow.packets)
            iats.append(flow.timestamp)
'''

content = re.sub(r'        for flow in flows:.*?            iats\.append\(flow\.timestamp\)', new_acc, content, flags=re.DOTALL)

# Update directionality mathematically: (orig_packets - resp_packets) / (orig_packets + resp_packets)
new_dir = '''        directionality = 0.0
        if packet_count > 0:
            directionality = (src_packet_count - dst_packet_count) / packet_count'''

content = re.sub(r'        directionality = 0\.0\n        if dst_packet_count \+ src_packet_count > 0:\n            directionality = \(src_packet_count - dst_packet_count\) / \(src_packet_count \+ dst_packet_count\)', new_dir, content, flags=re.DOTALL)

with open('backend/ml/feature_engine.py', 'w') as f:
    f.write(content)
