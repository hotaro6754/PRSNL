from typing import List, Dict
import math

def _flow_attr(flow, attr, default=None):
    if isinstance(flow, dict):
        return flow.get(attr, default)
    return getattr(flow, attr, default)

def flow_id_string(flow) -> str:
    proto = _flow_attr(flow, "protocol")
    if proto == 6: proto_name = "TCP"
    elif proto == 17: proto_name = "UDP"
    elif proto == 1: proto_name = "ICMP"
    else: proto_name = f"PROTO_{proto}"
    
    return f"{_flow_attr(flow, 'src_ip')}:{_flow_attr(flow, 'src_port')} -> {_flow_attr(flow, 'dst_ip')}:{_flow_attr(flow, 'dst_port')} {proto_name}"

def entropy_of_values(values: List) -> float:
    if not values:
        return 0.0
    from collections import Counter
    counts = Counter(values)
    total = len(values)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def compute_window_stats(flows: List) -> Dict:
    if not flows:
        return {}
    
    total_packets = 0
    total_bytes = 0
    src_ips = []
    dst_ips = []
    dst_ports = []
    syn_like_count = 0
    
    min_ts = float('inf')
    max_ts = 0
    
    for f in flows:
        total_packets += _flow_attr(f, "bidirectional_packets", 0)
        total_bytes += _flow_attr(f, "bidirectional_bytes", 0)
        src_ips.append(_flow_attr(f, "src_ip"))
        dst_ips.append(_flow_attr(f, "dst_ip"))
        dst_ports.append(_flow_attr(f, "dst_port"))
        
        if _flow_attr(f, "protocol") == 6 and _flow_attr(f, "src2dst_packets", 0) > _flow_attr(f, "dst2src_packets", 0):
            syn_like_count += 1
            
        ts = _flow_attr(f, "bidirectional_first_seen_ms", 0)
        if ts < min_ts: min_ts = ts
        if ts > max_ts: max_ts = ts
        
    duration_sec = (max_ts - min_ts) / 1000.0 if max_ts > min_ts else 1.0
    if duration_sec == 0:
        duration_sec = 1.0
        
    return {
        "total_packets": total_packets,
        "total_bytes": total_bytes,
        "unique_src_ips": len(set(src_ips)),
        "unique_dst_ips": len(set(dst_ips)),
        "unique_dst_ports": len(set(dst_ports)),
        "syn_like_count": syn_like_count,
        "flow_count": len(flows),
        "src_ip_entropy": entropy_of_values(src_ips),
        "pps": total_packets / duration_sec,
        "bps": (total_bytes * 8) / duration_sec
    }
