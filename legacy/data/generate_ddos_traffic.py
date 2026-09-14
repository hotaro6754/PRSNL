import time
from scapy.all import IP, TCP, UDP, wrpcap

def generate_benign_transfer():
    """Generates a benign high-throughput file transfer (High BPS, low SYN ratio)."""
    pkts = []
    base_time = time.time()
    # Initial SYN
    pkts.append(IP(src="192.168.1.50", dst="10.0.0.5") / TCP(sport=12345, dport=443, flags="S"))
    pkts[-1].time = base_time
    
    # Massive payload ACKs
    for i in range(1, 1000):
        pkt = IP(src="192.168.1.50", dst="10.0.0.5") / TCP(sport=12345, dport=443, flags="A") / (b"A" * 1400)
        pkt.time = base_time + (i * 0.001) # 1ms apart, 1000 pps, ~11Mbps
        pkts.append(pkt)
    wrpcap("data/pcaps/benign_transfer.pcap", pkts)
    print(f"Generated {len(pkts)} packets for benign_transfer.pcap")

def generate_syn_flood():
    """Generates a spoofed SYN flood (High PPS, High Cardinality, 100% SYN)."""
    pkts = []
    base_time = time.time()
    for i in range(1, 1000):
        spoofed_src = f"10.1.{i%255}.{i%255}"
        pkt = IP(src=spoofed_src, dst="10.0.0.5") / TCP(sport=10000+(i%1000), dport=80, flags="S")
        pkt.time = base_time + (i * 0.001)
        pkts.append(pkt)
    wrpcap("data/pcaps/syn_flood.pcap", pkts)
    print(f"Generated {len(pkts)} packets for syn_flood.pcap")

def generate_udp_flood():
    """Generates a UDP flood (High PPS, UDP protocol)."""
    pkts = []
    base_time = time.time()
    for i in range(1, 1000):
        pkt = IP(src="192.168.1.99", dst="10.0.0.5") / UDP(sport=53, dport=12345) / (b"X" * 500)
        pkt.time = base_time + (i * 0.001)
        pkts.append(pkt)
    wrpcap("data/pcaps/udp_flood.pcap", pkts)
    print(f"Generated {len(pkts)} packets for udp_flood.pcap")

if __name__ == "__main__":
    generate_benign_transfer()
    generate_syn_flood()
    generate_udp_flood()
