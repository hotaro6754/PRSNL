import sys
import os
import time
import uuid
import json
import random
from kafka import KafkaProducer

def make_obs(**kwargs):
    now_ms = int(time.time() * 1000)
    defaults = dict(
        observation_id=str(uuid.uuid4()),
        flow_id=str(uuid.uuid4())[:8],
        timestamp=now_ms,
        first_seen=now_ms,
        last_seen=now_ms + 1000,
        duration=1.0,
        source_ip="192.168.1.10",
        destination_ip="10.0.0.1",
        source_port=random.randint(1024, 65535),
        destination_port=80,
        protocol=6,
        orig_packets=10,
        resp_packets=8,
        orig_ip_bytes=1000,
        resp_ip_bytes=5000,
        tcp_syn_orig=True,
        tcp_syn_resp=True,
        tcp_fin_orig=True,
        tcp_fin_resp=True,
        tcp_rst_orig=False,
        tcp_rst_resp=False,
    )
    defaults.update(kwargs)
    return defaults

def generate_flows():
    now_ms = int(time.time() * 1000)
    flows = []
    
    # T1
    flows.extend([make_obs(destination_port=443, orig_ip_bytes=2000, resp_ip_bytes=50000) for _ in range(3)])
    # T2
    flows.extend([make_obs(destination_port=443, orig_ip_bytes=50000, resp_ip_bytes=500000, orig_packets=100, resp_packets=200) for _ in range(8)])
    # T3 SYN
    flows.extend([make_obs(source_ip=f"10.0.{random.randint(0,255)}.{random.randint(1,254)}", orig_packets=1, resp_packets=0, orig_ip_bytes=54, resp_ip_bytes=0, tcp_syn_orig=True, tcp_syn_resp=False, tcp_fin_orig=False, tcp_fin_resp=False, duration=0.01) for _ in range(600)])
    # T4 UDP
    flows.extend([make_obs(protocol=17, destination_port=53, orig_packets=2, resp_packets=0, orig_ip_bytes=1200, resp_ip_bytes=0, tcp_syn_orig=False, tcp_syn_resp=False, tcp_fin_orig=False, tcp_fin_resp=False) for _ in range(600)])
    # T5 Beacon
    flows.extend([make_obs(destination_ip="203.0.113.5", destination_port=443, orig_ip_bytes=200, resp_ip_bytes=100, duration=0.5, timestamp=now_ms + (i * 5000), bidirectional_bytes=300) for i in range(20)])
    # T6 Jittered
    flows.extend([make_obs(destination_ip="203.0.113.10", destination_port=8443, orig_ip_bytes=150, resp_ip_bytes=80, timestamp=now_ms + int((i * 5000) + random.uniform(-500, 500)), bidirectional_bytes=230) for i in range(15)])
    # T7 DGA
    flows.extend([make_obs(protocol=17, destination_port=53, dns_query=f"q9x3vj8k2m5z7w4n1p6r8t4y2u1o9.com", orig_ip_bytes=80, resp_ip_bytes=200, tcp_syn_orig=False, tcp_syn_resp=False, tcp_fin_orig=False, tcp_fin_resp=False, orig_packets=1, resp_packets=1) for _ in range(20)])
    # T8 DNS Tunnel
    flows.extend([make_obs(protocol=17, destination_port=53, dns_query=f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=50))}.tunnel.example.com", orig_ip_bytes=300, resp_ip_bytes=50, tcp_syn_orig=False, tcp_syn_resp=False, tcp_fin_orig=False, tcp_fin_resp=False, orig_packets=1, resp_packets=1) for _ in range(25)])
    # T9 Encrypted Session
    flows.extend([make_obs(destination_ip="10.0.0.9", destination_port=443, tls_ja3="a0e9f5d64349fb13191bc781f81f42e1", tls_sni="suspicious-c2.example.com", orig_ip_bytes=500, resp_ip_bytes=200, bidirectional_bytes=700, timestamp=now_ms + (i * 1000)) for i in range(15)])
    # T10 Port Scan
    flows.extend([make_obs(destination_ip="10.0.0.50", destination_port=i * 100 + 1, orig_packets=1, resp_packets=0, orig_ip_bytes=54, resp_ip_bytes=0, tcp_fin_orig=False, tcp_fin_resp=False, duration=0.01) for i in range(1, 30)])
    # T11 Slow Scan
    flows.extend([make_obs(destination_ip=f"10.0.0.{i}", destination_port=22, orig_packets=1, resp_packets=0, orig_ip_bytes=54, resp_ip_bytes=0, tcp_fin_orig=False, tcp_fin_resp=False, duration=0.01) for i in range(1, 10)])
    # T12 Exfil
    flows.extend([make_obs(destination_port=443, orig_ip_bytes=1500000, resp_ip_bytes=1000, orig_packets=1000, resp_packets=10)])
    # T13 Slowloris
    flows.extend([make_obs(source_ip="192.168.1.150", destination_ip="10.0.0.80", source_port=10000 + i, destination_port=80, orig_packets=3, resp_packets=1, orig_ip_bytes=120, resp_ip_bytes=40, tcp_fin_orig=False, tcp_fin_resp=False, duration=60.0) for i in range(50)])
    # T14 High Fanout Benign
    flows.extend([make_obs(destination_ip=f"10.0.{i // 256}.{i % 256}", destination_port=443, orig_ip_bytes=5000, resp_ip_bytes=50000, orig_packets=20, resp_packets=50) for i in range(30)])
    # T15 Spoofed SYN Flood
    flows.extend([make_obs(source_ip=f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}", destination_ip="192.168.1.1", orig_packets=1, resp_packets=0, orig_ip_bytes=54, resp_ip_bytes=0, tcp_syn_orig=True, tcp_syn_resp=False, tcp_fin_orig=False, tcp_fin_resp=False, duration=0.01) for _ in range(600)])
    
    return flows

if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers=['localhost:19092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print("Injecting T1-T15 Regression flows into Live Pipeline...")
    flows = generate_flows()
    random.shuffle(flows)
    
    for f in flows:
        producer.send('network-observations', f)
    
    producer.flush()
    print(f"Injected {len(flows)} flows successfully. Check the dashboard!")
