from pydantic import BaseModel
from typing import Optional

class FeatureVector(BaseModel):
    window_duration: float
    packet_count: int
    byte_count: int
    src_packet_count: int
    dst_packet_count: int
    src_byte_count: int
    dst_byte_count: int
    
    packet_size_mean: float
    packet_size_std: float
    packet_size_min: float
    packet_size_max: float
    
    iat_mean: float
    iat_std: float
    iat_cv: float
    
    packet_rate: float
    byte_rate: float
    
    syn_ratio: float
    fin_ratio: float
    rst_ratio: float
    
    udp_ratio: float
    tcp_ratio: float
    icmp_ratio: float
    
    directionality: float
    fan_in: int
    fan_out: int
    
    dns_entropy: float
    tls_sni_entropy: float
    
    # --- Entity / Host Baseline Features (Layer 2) ---
    host_connections_5m: int = 0
    host_unique_dests_5m: int = 0
    host_unique_ports_5m: int = 0
    host_dns_queries_5m: int = 0
    host_tls_connections_5m: int = 0
    host_bytes_out_5m: int = 0
    host_bytes_in_5m: int = 0
    
    host_connections_1h: int = 0
    host_unique_dests_1h: int = 0
    host_unique_ports_1h: int = 0
    host_dns_queries_1h: int = 0
    host_tls_connections_1h: int = 0
    host_bytes_out_1h: int = 0
    host_bytes_in_1h: int = 0
    
    host_connections_24h: int = 0
    host_unique_dests_24h: int = 0
    host_unique_ports_24h: int = 0
    host_dns_queries_24h: int = 0
    host_tls_connections_24h: int = 0
    host_bytes_out_24h: int = 0
    host_bytes_in_24h: int = 0

