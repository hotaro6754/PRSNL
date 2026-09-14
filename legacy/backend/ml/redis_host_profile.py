import redis
from typing import Dict
from backend.contracts.observation import NetworkObservation

class RedisHostBehaviorManager:
    """
    P2: Enterprise Horizontally Scalable Entity Baselines.
    Maintains 1m, 5m, 1h, and 24h rolling windows in O(1) read time
    by simultaneously incrementing hierarchical time buckets.
    """
    def __init__(self, redis_host: str = 'redis', redis_port: int = 6379):
        # Graceful fallback if Redis isn't reachable during static dev
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
            self.redis.ping()
            self.enabled = True
        except Exception:
            self.enabled = False

    def add_flow(self, flow: NetworkObservation):
        if not self.enabled or not flow.source_ip:
            return

        ts = flow.timestamp
        ip = flow.source_ip
        
        # Define hierarchical bucket resolutions
        buckets = {
            '1m': ts // 60000,
            '5m': ts // 300000,
            '1h': ts // 3600000,
            '24h': ts // 86400000
        }
        
        pipe = self.redis.pipeline()
        
        for res, bucket_id in buckets.items():
            base_key = f"host:{ip}:{res}:{bucket_id}"
            
            pipe.hincrby(base_key, "conns", 1)
            pipe.hincrby(base_key, "bytes_out", flow.orig_ip_bytes)
            pipe.hincrby(base_key, "bytes_in", flow.resp_ip_bytes)
            
            if flow.dns_query:
                pipe.hincrby(base_key, "dns", 1)
            if flow.tls_ja3 or flow.tls_sni or flow.destination_port in [443, 8443]:
                pipe.hincrby(base_key, "tls", 1)
                
            if flow.destination_ip:
                pipe.pfadd(f"{base_key}:dests", flow.destination_ip)
            if flow.destination_port:
                pipe.pfadd(f"{base_key}:ports", str(flow.destination_port))
                
            # Expirations (buffer added to each)
            ttl = 86400 + 3600 if res == '24h' else (3600 + 300 if res == '1h' else 600)
            pipe.expire(base_key, ttl)
            pipe.expire(f"{base_key}:dests", ttl)
            pipe.expire(f"{base_key}:ports", ttl)
            
        pipe.execute()

    def get_features(self, ip: str, current_ts_ms: int) -> Dict[str, int]:
        default_feat = {
            "connections_5m": 0, "unique_dests_5m": 0, "unique_ports_5m": 0, "dns_queries_5m": 0, "tls_connections_5m": 0, "bytes_out_5m": 0, "bytes_in_5m": 0,
            "connections_1h": 0, "unique_dests_1h": 0, "unique_ports_1h": 0, "dns_queries_1h": 0, "tls_connections_1h": 0, "bytes_out_1h": 0, "bytes_in_1h": 0,
            "connections_24h": 0, "unique_dests_24h": 0, "unique_ports_24h": 0, "dns_queries_24h": 0, "tls_connections_24h": 0, "bytes_out_24h": 0, "bytes_in_24h": 0,
        }
        
        if not self.enabled:
            return default_feat

        buckets = {
            '5m': current_ts_ms // 300000,
            '1h': current_ts_ms // 3600000,
            '24h': current_ts_ms // 86400000
        }
        
        pipe = self.redis.pipeline()
        for res, bucket_id in buckets.items():
            base = f"host:{ip}:{res}:{bucket_id}"
            pipe.hgetall(base)
            pipe.pfcount(f"{base}:dests")
            pipe.pfcount(f"{base}:ports")
            
        results = pipe.execute()
        
        out = {}
        for i, res in enumerate(['5m', '1h', '24h']):
            h = results[i*3] or {}
            dests = results[i*3 + 1] or 0
            ports = results[i*3 + 2] or 0
            
            out[f"connections_{res}"] = int(h.get("conns", 0))
            out[f"bytes_out_{res}"] = int(h.get("bytes_out", 0))
            out[f"bytes_in_{res}"] = int(h.get("bytes_in", 0))
            out[f"dns_queries_{res}"] = int(h.get("dns", 0))
            out[f"tls_connections_{res}"] = int(h.get("tls", 0))
            out[f"unique_dests_{res}"] = dests
            out[f"unique_ports_{res}"] = ports
            
        return out
