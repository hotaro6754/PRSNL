import os

with open('backend/ml/router.py', 'r') as f:
    content = f.read()
    
# Replace FEATURE_COLUMNS
import re
new_cols = '''FEATURE_COLUMNS = [
    "window_duration",
    "packet_count",
    "byte_count",
    "src_packet_count",
    "dst_packet_count",
    "src_byte_count",
    "dst_byte_count",
    "packet_size_mean",
    "packet_size_std",
    "packet_size_min",
    "packet_size_max",
    "iat_mean",
    "iat_std",
    "iat_cv",
    "packet_rate",
    "byte_rate",
    "syn_ratio",
    "fin_ratio",
    "rst_ratio",
    "udp_ratio",
    "tcp_ratio",
    "icmp_ratio",
    "directionality",
    "fan_in",
    "fan_out",
    "dns_entropy",
    "tls_sni_entropy"
]'''

content = re.sub(r'FEATURE_COLUMNS = \[.*?\]', new_cols, content, flags=re.DOTALL)

with open('backend/ml/router.py', 'w') as f:
    f.write(content)
