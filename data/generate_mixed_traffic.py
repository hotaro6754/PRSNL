import time
from scapy.all import IP, TCP, wrpcap

def generate_benign_web():
    """Generates 100 connections from 1 source to 100 different IPs on port 443."""
    pkts = []
    base_time = time.time()
    for i in range(1, 101):
        dst_ip = f"104.21.33.{i}"
        sport = 50000+i
        # Send SYN
        pkt1 = IP(src="192.168.1.10", dst=dst_ip) / TCP(sport=sport, dport=443, flags="S")
        pkt1.time = base_time + (i * 0.05)
        pkts.append(pkt1)
        # Send ACK
        pkt2 = IP(src="192.168.1.10", dst=dst_ip) / TCP(sport=sport, dport=443, flags="A")
        pkt2.time = base_time + (i * 0.05) + 0.01
        pkts.append(pkt2)
        # Send PSH/ACK (Data)
        pkt3 = IP(src="192.168.1.10", dst=dst_ip) / TCP(sport=sport, dport=443, flags="PA") / b"GET / HTTP/1.1\r\n"
        pkt3.time = base_time + (i * 0.05) + 0.02
        pkts.append(pkt3)
    pkts.sort(key=lambda x: x.time)
    wrpcap("data/pcaps/benign_web.pcap", pkts)
    print(f"Generated {len(pkts)} packets for benign_web.pcap")

def generate_stealth_scan():
    """Generates a vertical port scan (50 ports) spread over 2 minutes (too slow for a 10s window)."""
    pkts = []
    base_time = time.time()
    for port in range(1, 51):
        pkt = IP(src="10.0.0.99", dst="192.168.1.5") / TCP(sport=20000+port, dport=port, flags="S")
        pkt.time = base_time + (port * 2.5) # 2.5 seconds apart
        pkts.append(pkt)
    wrpcap("data/pcaps/stealth_scan.pcap", pkts)
    print(f"Generated {len(pkts)} packets for stealth_scan.pcap")

def generate_mixed_noise():
    """Generates benign web browsing PLUS a fast horizontal scan on port 22."""
    pkts = []
    base_time = time.time()
    
    # Benign web traffic (100 connections)
    for i in range(1, 101):
        dst_ip = f"104.21.33.{i}"
        sport = 50000+i
        pkt1 = IP(src="192.168.1.10", dst=dst_ip) / TCP(sport=sport, dport=443, flags="S")
        pkt1.time = base_time + (i * 0.05)
        pkts.append(pkt1)
        pkt2 = IP(src="192.168.1.10", dst=dst_ip) / TCP(sport=sport, dport=443, flags="A")
        pkt2.time = base_time + (i * 0.05) + 0.01
        pkts.append(pkt2)
        pkt3 = IP(src="192.168.1.10", dst=dst_ip) / TCP(sport=sport, dport=443, flags="PA") / b"GET / HTTP/1.1\r\n"
        pkt3.time = base_time + (i * 0.05) + 0.02
        pkts.append(pkt3)
        
    # Horizontal SSH scan (192.168.1.100 scanning 50 internal IPs on port 22)
    for i in range(1, 51):
        dst_ip = f"10.0.0.{i}"
        pkt = IP(src="192.168.1.100", dst=dst_ip) / TCP(sport=30000+i, dport=22, flags="S")
        pkt.time = base_time + 2.0 + (i * 0.02) # Starts 2 seconds in, very fast
        pkts.append(pkt)
        
    # Sort by time to be strictly chronological for the tumbling window
    pkts.sort(key=lambda x: x.time)
    
    wrpcap("data/pcaps/mixed_noise.pcap", pkts)
    print(f"Generated {len(pkts)} packets for mixed_noise.pcap")

if __name__ == "__main__":
    generate_benign_web()
    generate_stealth_scan()
    generate_mixed_noise()
