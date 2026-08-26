import time
import random
from scapy.all import IP, UDP, DNS, DNSQR, wrpcap

def generate_benign_dns():
    """Generates normal browsing DNS and CDN requests (False Positive tests)."""
    pkts = []
    base_time = time.time()
    
    domains = [
        "www.google.com", 
        "amazon.com", 
        "mail.yahoo.com",
        "a1b2c3d4.cloudfront.net", # High entropy CDN, should not flag if digit ratio is balanced
        "static-assets-x293.fbcdn.net"
    ]
    
    for i, domain in enumerate(domains):
        pkt = IP(src="192.168.1.10", dst="8.8.8.8") / UDP(sport=50000+i, dport=53) / DNS(rd=1, qd=DNSQR(qname=domain))
        pkt.time = base_time + i
        pkts.append(pkt)
        
    wrpcap("data/pcaps/benign_dns.pcap", pkts)
    print(f"Generated {len(pkts)} packets for benign_dns.pcap")

def generate_dga_dns():
    """Generates DGA-like requests (True Positive test for stateless DGA)."""
    pkts = []
    base_time = time.time()
    
    # Pure consonant DGA (Conficker-like)
    domain1 = "kxjhqzvbmrtp.com" 
    pkt1 = IP(src="192.168.1.11", dst="8.8.8.8") / UDP(sport=50001, dport=53) / DNS(rd=1, qd=DNSQR(qname=domain1))
    pkt1.time = base_time + 1
    pkts.append(pkt1)
    
    # Alphanumeric DGA with high digit ratio
    domain2 = "a1b2c3d4e5f6g7h8i9j0.net"
    pkt2 = IP(src="192.168.1.11", dst="8.8.8.8") / UDP(sport=50002, dport=53) / DNS(rd=1, qd=DNSQR(qname=domain2))
    pkt2.time = base_time + 2
    pkts.append(pkt2)
    
    # Extreme length DGA
    domain3 = "thisisareallylongdomainnamethatmakesnosenseatallbutisusedbybotnets.org"
    pkt3 = IP(src="192.168.1.11", dst="8.8.8.8") / UDP(sport=50003, dport=53) / DNS(rd=1, qd=DNSQR(qname=domain3))
    pkt3.time = base_time + 3
    pkts.append(pkt3)

    wrpcap("data/pcaps/dga_botnet.pcap", pkts)
    print(f"Generated {len(pkts)} packets for dga_botnet.pcap")

def generate_dns_tunnel():
    """Generates DNS Tunnelling (True Positive test for stateful tunnel)."""
    pkts = []
    base_time = time.time()
    
    root_domain = "tunnel.com"
    # Send 25 queries, each with a 50-character unique subdomain (payload)
    # Total payload = 1250 bytes. Exceeds max_unique (20) and min_bytes (1000).
    for i in range(25):
        payload = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=50))
        domain = f"{payload}.{root_domain}"
        
        pkt = IP(src="192.168.1.12", dst="8.8.8.8") / UDP(sport=50000+i, dport=53) / DNS(rd=1, qd=DNSQR(qname=domain))
        pkt.time = base_time + (i * 2) # Every 2 seconds
        pkts.append(pkt)

    wrpcap("data/pcaps/dns_tunnel.pcap", pkts)
    print(f"Generated {len(pkts)} packets for dns_tunnel.pcap")

if __name__ == "__main__":
    generate_benign_dns()
    generate_dga_dns()
    generate_dns_tunnel()
