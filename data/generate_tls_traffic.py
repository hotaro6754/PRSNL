import time
import random
from scapy.all import IP, TCP, wrpcap, load_layer

# Load TLS layer for Scapy
load_layer("tls")
from scapy.layers.tls.handshake import TLSClientHello
from scapy.layers.tls.extensions import TLS_Ext_ServerName, ServerName
from scapy.layers.tls.record import TLS

def generate_benign_https():
    """Generates standard browser HTTPS traffic (high size variance, varying timing)."""
    pkts = []
    base_time = time.time()
    
    for i in range(15):
        # Varying payload sizes (e.g. downloading images vs HTML)
        size = random.randint(100, 1500)
        
        # Consistent JA3 configuration (Chrome-like)
        ch = TLSClientHello(version=0x0303, ciphers=[0xc02b, 0xc02f, 0xcca9])
        sni = TLS_Ext_ServerName(servernames=[ServerName(servername=b"www.google.com")])
        ch.ext = [sni]
        
        pkt = IP(src="192.168.1.10", dst="104.20.10.1") / TCP(sport=50000, dport=443) / TLS(msg=[ch]) / (b"X" * size)
        
        # Varying timing
        pkt.time = base_time + (i * 2) + random.uniform(0.1, 5.0) 
        pkts.append(pkt)

    wrpcap("data/pcaps/benign_https.pcap", pkts)
    print(f"Generated {len(pkts)} packets for benign_https.pcap")

def generate_benign_api():
    """Generates automated API polling (rigid timing, high size variance)."""
    pkts = []
    base_time = time.time()
    
    for i in range(15):
        # API payloads vary based on JSON length
        size = random.randint(200, 800)
        
        ch = TLSClientHello(version=0x0303, ciphers=[0xc02b])
        sni = TLS_Ext_ServerName(servernames=[ServerName(servername=b"api.weather.com")])
        ch.ext = [sni]
        
        pkt = IP(src="192.168.1.10", dst="104.20.10.2") / TCP(sport=50001, dport=443) / TLS(msg=[ch]) / (b"X" * size)
        
        # Rigid 30s polling
        pkt.time = base_time + (i * 30)
        pkts.append(pkt)

    wrpcap("data/pcaps/benign_api.pcap", pkts)
    print(f"Generated {len(pkts)} packets for benign_api.pcap")

def generate_encrypted_c2():
    """Generates Encrypted C2 beaconing (rigid timing, perfectly identical packet sizes, consistent JA3)."""
    pkts = []
    base_time = time.time()
    
    for i in range(15):
        # Beacon payload is identically sized
        size = 64
        
        ch = TLSClientHello(version=0x0303, ciphers=[0x00ff]) # Suspicious single cipher
        sni = TLS_Ext_ServerName(servernames=[ServerName(servername=b"update.evil.com")])
        ch.ext = [sni]
        
        pkt = IP(src="192.168.1.12", dst="185.10.10.1") / TCP(sport=50002, dport=443) / TLS(msg=[ch]) / (b"X" * size)
        
        # Rigid 60s polling
        pkt.time = base_time + (i * 60)
        pkts.append(pkt)

    wrpcap("data/pcaps/encrypted_c2.pcap", pkts)
    print(f"Generated {len(pkts)} packets for encrypted_c2.pcap")

def generate_jittered_encrypted_c2():
    """Generates Encrypted C2 beaconing with timing jitter, but rigid packet sizes."""
    pkts = []
    base_time = time.time()
    current_time = base_time
    
    for i in range(15):
        # Beacon payload is identically sized
        size = 64
        
        ch = TLSClientHello(version=0x0303, ciphers=[0x00ff])
        sni = TLS_Ext_ServerName(servernames=[ServerName(servername=b"update2.evil.com")])
        ch.ext = [sni]
        
        pkt = IP(src="192.168.1.13", dst="185.10.10.2") / TCP(sport=50003, dport=443) / TLS(msg=[ch]) / (b"X" * size)
        
        pkt.time = current_time
        pkts.append(pkt)
        
        # 60s polling with 15% jitter
        jitter = random.uniform(-0.15, 0.15) * 60
        current_time += (60 + jitter)

    wrpcap("data/pcaps/jittered_encrypted_c2.pcap", pkts)
    print(f"Generated {len(pkts)} packets for jittered_encrypted_c2.pcap")


if __name__ == "__main__":
    generate_benign_https()
    generate_benign_api()
    generate_encrypted_c2()
    generate_jittered_encrypted_c2()
