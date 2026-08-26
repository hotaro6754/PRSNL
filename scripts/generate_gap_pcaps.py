from scapy.all import *
import time

def generate_exfil():
    print("Generating Exfiltration PCAP...")
    pkts = []
    src = "192.168.1.100"
    dst = "10.0.0.50"
    # Small request
    pkts.append(IP(src=src, dst=dst)/TCP(sport=4444, dport=443, flags="S"))
    pkts.append(IP(src=dst, dst=src)/TCP(sport=443, dport=4444, flags="SA"))
    pkts.append(IP(src=src, dst=dst)/TCP(sport=4444, dport=443, flags="A"))
    
    # Large outbound (exfil)
    payload_out = b"A" * 1400
    for i in range(1000): # ~1.4MB out
        pkts.append(IP(src=src, dst=dst)/TCP(sport=4444, dport=443, flags="PA")/Raw(load=payload_out))
        if i % 100 == 0:
            pkts.append(IP(src=dst, dst=src)/TCP(sport=443, dport=4444, flags="A")) # Small ACKs in
            
    wrpcap("data/pcaps/exfil_test.pcap", pkts)

def generate_udp_reflection():
    print("Generating UDP Reflection PCAP...")
    pkts = []
    # Attacker spoofed source = victim (192.168.1.200)
    # Amplifiers (10.0.0.2 to 10.0.0.10)
    victim = "192.168.1.200"
    amplifiers = [f"10.0.0.{i}" for i in range(2, 12)]
    
    # Simulating the responses hitting the victim (amplification)
    # The Zeek sensor sees large UDP packets hitting the victim from multiple sources
    payload_amp = b"X" * 1200
    for _ in range(500):
        for amp in amplifiers:
            pkts.append(IP(src=amp, dst=victim)/UDP(sport=53, dport=40000)/Raw(load=payload_amp))
            
    wrpcap("data/pcaps/udp_reflection_test.pcap", pkts)
    
def generate_slowloris():
    print("Generating Slowloris PCAP...")
    pkts = []
    src = "192.168.1.150"
    dst = "10.0.0.80"
    # Multiple connections kept alive with tiny incomplete payloads
    for port in range(10000, 10050):
        pkts.append(IP(src=src, dst=dst)/TCP(sport=port, dport=80, flags="S"))
        pkts.append(IP(src=dst, dst=src)/TCP(sport=80, dport=port, flags="SA"))
        pkts.append(IP(src=src, dst=dst)/TCP(sport=port, dport=80, flags="A"))
        
        # Incomplete HTTP GET
        pkts.append(IP(src=src, dst=dst)/TCP(sport=port, dport=80, flags="PA")/Raw(load=b"GET / HTTP/1.1\r\n"))
    
    # Send tiny keep-alives slowly
    for i in range(5):
        for port in range(10000, 10050):
            pkts.append(IP(src=src, dst=dst)/TCP(sport=port, dport=80, flags="PA")/Raw(load=f"X-a: {i}\r\n".encode()))
            
    wrpcap("data/pcaps/slowloris_test.pcap", pkts)

if __name__ == "__main__":
    generate_exfil()
    generate_udp_reflection()
    generate_slowloris()
