import re

with open('backend/ml/router.py', 'r') as f:
    content = f.read()

new_cols = '''    "tls_sni_entropy",
    "host_connections_5m",
    "host_unique_dests_5m",
    "host_unique_ports_5m",
    "host_dns_queries_5m",
    "host_tls_connections_5m",
    "host_bytes_out_5m",
    "host_bytes_in_5m"
]'''

content = content.replace('    "tls_sni_entropy"\n]', new_cols)

with open('backend/ml/router.py', 'w') as f:
    f.write(content)
