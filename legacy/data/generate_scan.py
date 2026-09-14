from scapy.all import IP, TCP, wrpcap
import time

def generate_port_scan_pcap(filename):
    pkts = []
    src_ip = "192.168.1.50"
    dst_ip = "10.0.0.1"
    
    # 50 ports scanned very quickly (within 1 second)
    base_time = time.time()
    for port in range(1, 51):
        pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=10000+port, dport=port, flags="S")
        pkt.time = base_time + (port * 0.01) # 10ms apart
        pkts.append(pkt)
        
    wrpcap(filename, pkts)
    print(f"Generated {len(pkts)} packets to {filename}")

if __name__ == "__main__":
    generate_port_scan_pcap("data/pcaps/real_port_scan.pcap")
