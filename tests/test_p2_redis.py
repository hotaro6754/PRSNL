import time
from backend.contracts.observation import NetworkObservation
from backend.ml.redis_host_profile import RedisHostBehaviorManager

def test_hierarchy():
    manager = RedisHostBehaviorManager(redis_host='localhost', redis_port=6379)
    # Even if redis isn't running, it gracefully returns empty default features
    print(f"Redis Enabled: {manager.enabled}")
    
    # Simulate a flow
    flow = NetworkObservation(
        timestamp=int(time.time() * 1000),
        source_ip="192.168.1.10",
        destination_ip="10.0.0.1",
        destination_port=443,
        protocol=6,
        bidirectional_bytes=1500,
        orig_ip_bytes=500,
        resp_ip_bytes=1000,
        packets=3,
        tls_sni="evil.com",
        dns_query=""
    )
    
    manager.add_flow(flow)
    
    feat = manager.get_features("192.168.1.10", flow.timestamp)
    print("Features extracted successfully.")
    for k in ['connections_5m', 'connections_1h', 'connections_24h']:
        print(f"{k}: {feat.get(k)}")
        
if __name__ == '__main__':
    test_hierarchy()
