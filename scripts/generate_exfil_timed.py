from scapy.all import *
import time

def generate_exfil_timed():
    print("Generating Exfiltration PCAP with 65s duration...")
    pkts = []
    src = "192.168.1.100"
    dst = "10.0.0.50"
    
    # We will simulate timestamps
    base_time = time.time() - 1000
    
    p1 = IP(src=src, dst=dst)/TCP(sport=4444, dport=443, flags="S")
    p1.time = base_time
    pkts.append(p1)
    
    p2 = IP(src=dst, dst=src)/TCP(sport=443, dport=4444, flags="SA")
    p2.time = base_time + 0.1
    pkts.append(p2)
    
    p3 = IP(src=src, dst=dst)/TCP(sport=4444, dport=443, flags="A")
    p3.time = base_time + 0.2
    pkts.append(p3)
    
    payload_out = b"A" * 1400
    for i in range(1000): 
        pkt_time = base_time + 1.0 + (i * 0.06) # spreads over 60 seconds
        p = IP(src=src, dst=dst)/TCP(sport=4444, dport=443, flags="PA")/Raw(load=payload_out)
        p.time = pkt_time
        pkts.append(p)
        
        if i % 100 == 0:
            p_ack = IP(src=dst, dst=src)/TCP(sport=443, dport=4444, flags="A")
            p_ack.time = pkt_time + 0.01
            pkts.append(p_ack)
            
    # Send one more packet 65 seconds later to force window flush
    p_flush = IP(src=src, dst="10.0.0.99")/TCP(sport=4444, dport=80, flags="S")
    p_flush.time = base_time + 65.0
    pkts.append(p_flush)

    wrpcap("data/pcaps/exfil_timed.pcap", pkts)

if __name__ == "__main__":
    generate_exfil_timed()
