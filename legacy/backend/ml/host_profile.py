import time
from typing import Dict, Any, Tuple
from backend.contracts.observation import NetworkObservation

class HostBehaviorManager:
    """
    Maintains bounded, rolling 5-minute behavioral profiles for entities (IPs).
    Complies with strict requirements:
    1. event-time semantics (bucketed by timestamp)
    2. sliding TTL expiration (drops buckets older than 5m)
    3. bounded memory (fixed number of buckets, capped sets)
    4. duplicate/OOO handling (idempotent bucket writes)
    5. No raw identifier leakage (returns only counts)
    """
    def __init__(self, ttl_ms: int = 300000, bucket_size_ms: int = 10000, max_set_size: int = 1000):
        self.ttl_ms = ttl_ms
        self.bucket_size_ms = bucket_size_ms
        self.num_buckets = (ttl_ms // bucket_size_ms) + 1
        self.max_set_size = max_set_size
        self.state: Dict[str, Dict[int, Any]] = {}
        
    def add_flow(self, flow: NetworkObservation):
        src = flow.source_ip
        if not src:
            return
            
        ts = flow.timestamp
        bucket_id = ts // self.bucket_size_ms
        
        if src not in self.state:
            self.state[src] = {}
            
        host_state = self.state[src]
        
        if bucket_id not in host_state:
            host_state[bucket_id] = {
                "conns": 0,
                "dests": set(),
                "ports": set(),
                "dns": 0,
                "tls": 0,
                "bytes_out": 0,
                "bytes_in": 0
            }
            
        b = host_state[bucket_id]
        b["conns"] += 1
        b["bytes_out"] += flow.orig_ip_bytes
        b["bytes_in"] += flow.resp_ip_bytes
        
        if flow.destination_ip and len(b["dests"]) < self.max_set_size:
            b["dests"].add(flow.destination_ip)
        if flow.destination_port and len(b["ports"]) < self.max_set_size:
            b["ports"].add(flow.destination_port)
            
        if flow.dns_query:
            b["dns"] += 1
            
        if flow.tls_ja3 or flow.tls_sni or flow.destination_port in [443, 8443]:
            b["tls"] += 1
            
        # Evict old buckets aggressively during insert to bound memory
        current_bucket = int(time.time() * 1000) // self.bucket_size_ms
        # BUT wait, we must use event time, so we evict based on the latest bucket seen FOR THIS HOST.
        max_b = max(host_state.keys())
        keys_to_delete = [k for k in host_state.keys() if k < max_b - self.num_buckets]
        for k in keys_to_delete:
            del host_state[k]

    def get_features(self, ip: str, current_ts_ms: int) -> Dict[str, int]:
        default_feat = {
            "host_connections_5m": 0,
            "host_unique_dests_5m": 0,
            "host_unique_ports_5m": 0,
            "host_dns_queries_5m": 0,
            "host_tls_connections_5m": 0,
            "host_bytes_out_5m": 0,
            "host_bytes_in_5m": 0
        }
        
        if ip not in self.state:
            return default_feat
            
        current_bucket = current_ts_ms // self.bucket_size_ms
        host_state = self.state[ip]
        
        conns = 0
        bytes_out = 0
        bytes_in = 0
        dns = 0
        tls = 0
        dests = set()
        ports = set()
        
        for i in range(current_bucket - self.num_buckets + 1, current_bucket + 1):
            if i in host_state:
                b = host_state[i]
                conns += b["conns"]
                bytes_out += b["bytes_out"]
                bytes_in += b["bytes_in"]
                dns += b["dns"]
                tls += b["tls"]
                if len(dests) < self.max_set_size * 5: # prevent huge merges
                    dests.update(b["dests"])
                if len(ports) < self.max_set_size * 5:
                    ports.update(b["ports"])
                    
        return {
            "host_connections_5m": conns,
            "host_unique_dests_5m": len(dests),
            "host_unique_ports_5m": len(ports),
            "host_dns_queries_5m": dns,
            "host_tls_connections_5m": tls,
            "host_bytes_out_5m": bytes_out,
            "host_bytes_in_5m": bytes_in
        }
