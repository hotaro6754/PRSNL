import time
from backend.contracts.observation import NetworkObservation
from backend.ml.host_profile import HostBehaviorManager

def make_obs(ts, src, dst, bytes_out=100):
    return NetworkObservation(
        observation_id="test", flow_id="test", timestamp=ts, first_seen=ts, last_seen=ts,
        duration=0, source_ip=src, destination_ip=dst, source_port=123, destination_port=80,
        protocol=6, orig_packets=1, resp_packets=1, orig_ip_bytes=bytes_out, resp_ip_bytes=0,
        tcp_syn_orig=True, tcp_syn_resp=False, tcp_fin_orig=False, tcp_fin_resp=False,
        tcp_rst_orig=False, tcp_rst_resp=False, dns_query=None, tls_sni=None,
        src2dst_bytes=bytes_out, dst2src_bytes=0, packets=2, bytes=bytes_out, 
        bidirectional_bytes=bytes_out, bidirectional_packets=2
    )

print('TEST 1: Canonical Bytes')
mgr = HostBehaviorManager()
mgr.add_flow(make_obs(1000, '1.1.1.1', '2.2.2.2', 500))
f = mgr.get_features('1.1.1.1', int(time.time() * 1000))
print(f"Bytes out: {f.get('host_bytes_out_5m', 0)}")

print('\\nTEST 2: Tumbling Window Expiration (Not Sliding)')
mgr = HostBehaviorManager(ttl_ms=5000) # 5 sec
mgr.add_flow(make_obs(1000, '1.1.1.2', '2.2.2.2'))
mgr.add_flow(make_obs(2000, '1.1.1.2', '3.3.3.3'))
mgr.add_flow(make_obs(3000, '1.1.1.2', '4.4.4.4'))
print(f"Conns at 3s: {mgr.get_features('1.1.1.2', 3000)['host_connections_5m']}")
mgr.add_flow(make_obs(7000, '1.1.1.2', '5.5.5.5'))
print(f"Conns at 7s: {mgr.get_features('1.1.1.2', 7000)['host_connections_5m']} (Expected: Should only drop the 1000ms flow, leaving 3. Actual: completely resets because 7000-1000 > 5000)")

print('\\nTEST 3: Out of Order')
mgr = HostBehaviorManager(ttl_ms=5000)
mgr.add_flow(make_obs(5000, '1.1.1.3', '2.2.2.2'))
mgr.add_flow(make_obs(1000, '1.1.1.3', '3.3.3.3')) # Arrives late
print(f"Conns with OOO: {mgr.get_features('1.1.1.3', 5000)['host_connections_5m']}")

