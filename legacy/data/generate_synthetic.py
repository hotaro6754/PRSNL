"""
Script to generate synthetic PCAPs for testing SIH 26145 detectors.
Generates:
1. Normal background traffic (HTTP/HTTPS)
2. SYN Flood (DDoS)
3. C2 Beaconing (Regular intervals)
4. DGA DNS Queries
5. Port Scanning
"""
import os
from scapy.all import IP, TCP, UDP, DNS, DNSQR, wrpcap
import time

def create_syn_flood():
    packets = []
    dst_ip = "10.0.0.5"
    for i in range(100):
        src_ip = f"192.168.1.{10 + (i % 50)}"
        pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=1024 + i, dport=80, flags="S")
        pkt.time = time.time() + (i * 0.01)
        packets.append(pkt)
    return packets

def create_port_scan():
    packets = []
    src_ip = "192.168.1.100"
    dst_ip = "10.0.0.5"
    for port in range(1, 100):
        pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=54321, dport=port, flags="S")
        pkt.time = time.time() + 2 + (port * 0.05)
        packets.append(pkt)
    return packets

def create_beaconing():
    packets = []
    src_ip = "10.0.0.10"
    dst_ip = "203.0.113.50"
    base_time = time.time() + 5
    for i in range(10):
        # Request
        pkt_req = IP(src=src_ip, dst=dst_ip) / TCP(sport=49152+i, dport=443, flags="PA") / b"Beacon"
        pkt_req.time = base_time + (i * 60) # Exactly 60s interval
        
        # Response
        pkt_res = IP(src=dst_ip, dst=src_ip) / TCP(sport=443, dport=49152+i, flags="PA") / b"Ack"
        pkt_res.time = base_time + (i * 60) + 0.1
        
        packets.extend([pkt_req, pkt_res])
    return packets

def create_dga_dns():
    packets = []
    src_ip = "10.0.0.15"
    dst_ip = "8.8.8.8"
    dga_domains = ["x7j2m5v8b4z1n3.com", "qwertyuiopasdfgh.net", "1234567890abcdef.org"]
    base_time = time.time() + 10
    
    for i, domain in enumerate(dga_domains):
        pkt = IP(src=src_ip, dst=dst_ip) / UDP(sport=33333+i, dport=53) / DNS(rd=1, qd=DNSQR(qname=domain))
        pkt.time = base_time + (i * 5)
        packets.append(pkt)
    return packets

def main():
    print("Generating synthetic traffic...")
    all_packets = []
    all_packets.extend(create_syn_flood())
    all_packets.extend(create_port_scan())
    all_packets.extend(create_beaconing())
    all_packets.extend(create_dga_dns())
    
    # Sort by time
    all_packets.sort(key=lambda p: p.time)
    
    out_dir = os.path.join(os.path.dirname(__file__), "pcaps")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "synthetic_attack.pcap")
    
    wrpcap(out_file, all_packets)
    print(f"Generated {len(all_packets)} packets -> {out_file}")

if __name__ == "__main__":
    main()
