import time
import random
from scapy.all import IP, TCP, UDP, wrpcap

def generate_ntp_polling():
    """Benign: Extremely rigid periodicity on Port 123 (NTP)."""
    pkts = []
    base_time = time.time()
    for i in range(10):
        pkt = IP(src="192.168.1.10", dst="8.8.8.8") / UDP(sport=123, dport=123) / (b"NTP" * 10)
        pkt.time = base_time + (i * 60) # Exactly 60s
        pkts.append(pkt)
    wrpcap("data/pcaps/ntp_polling.pcap", pkts)
    print(f"Generated {len(pkts)} packets for ntp_polling.pcap")

def generate_api_polling():
    """Benign: Periodic polling but highly variable payload sizes."""
    pkts = []
    base_time = time.time()
    for i in range(10):
        payload_size = random.randint(100, 1500)
        pkt = IP(src="192.168.1.15", dst="104.20.10.1") / TCP(sport=55555, dport=443, flags="PA") / (b"X" * payload_size)
        pkt.time = base_time + (i * 30) + random.uniform(-1, 1) # 30s avg, tiny jitter
        pkts.append(pkt)
    wrpcap("data/pcaps/api_polling.pcap", pkts)
    print(f"Generated {len(pkts)} packets for api_polling.pcap")

def generate_rigid_beacon():
    """Malicious: Standard rigid 60s HTTP beacon with exact sizes."""
    pkts = []
    base_time = time.time()
    for i in range(10):
        pkt = IP(src="10.0.0.50", dst="185.10.10.1") / TCP(sport=44444, dport=80, flags="PA") / (b"GET / HTTP/1.1\r\n\r\n")
        pkt.time = base_time + (i * 60)
        pkts.append(pkt)
    wrpcap("data/pcaps/rigid_beacon.pcap", pkts)
    print(f"Generated {len(pkts)} packets for rigid_beacon.pcap")

def generate_jittered_beacon():
    """Malicious: 60s beacon with 30% jitter."""
    pkts = []
    base_time = time.time()
    current_time = base_time
    for i in range(10):
        pkt = IP(src="10.0.0.60", dst="185.10.10.2") / TCP(sport=44445, dport=443, flags="PA") / (b"C2_PING")
        pkt.time = current_time
        pkts.append(pkt)
        
        # Add 60s + up to 30% jitter
        jitter = random.uniform(-0.3, 0.3) * 60
        current_time += (60 + jitter)
    wrpcap("data/pcaps/jittered_beacon.pcap", pkts)
    print(f"Generated {len(pkts)} packets for jittered_beacon.pcap")

def generate_slow_beacon():
    """Malicious: 300s (5-minute) slow beacon that crosses many tumbling windows."""
    pkts = []
    base_time = time.time()
    for i in range(6): # Needs 5 for detection
        pkt = IP(src="10.0.0.70", dst="185.10.10.3") / TCP(sport=44446, dport=443, flags="PA") / (b"PING")
        pkt.time = base_time + (i * 300)
        pkts.append(pkt)
    wrpcap("data/pcaps/slow_beacon.pcap", pkts)
    print(f"Generated {len(pkts)} packets for slow_beacon.pcap")

if __name__ == "__main__":
    generate_ntp_polling()
    generate_api_polling()
    generate_rigid_beacon()
    generate_jittered_beacon()
    generate_slow_beacon()
