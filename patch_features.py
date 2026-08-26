import re

with open('backend/contracts/features.py', 'r') as f:
    content = f.read()

new_features = '''    tls_sni_entropy: float
    
    # --- Entity / Host Baseline Features (Layer 2) ---
    host_connections_5m: int = 0
    host_unique_dests_5m: int = 0
    host_unique_ports_5m: int = 0
    host_dns_queries_5m: int = 0
    host_tls_connections_5m: int = 0
    host_bytes_out_5m: int = 0
    host_bytes_in_5m: int = 0
'''

content = content.replace('    tls_sni_entropy: float', new_features)

with open('backend/contracts/features.py', 'w') as f:
    f.write(content)
