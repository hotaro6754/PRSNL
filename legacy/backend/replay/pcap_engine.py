import logging
from typing import Iterator, Dict, Any
from scapy.all import PcapReader, IP, TCP, UDP, DNS, DNSQR, load_layer
import uuid
import time
import hashlib

# Load TLS layer for Scapy
load_layer("tls")
from scapy.layers.tls.handshake import TLSClientHello
from scapy.layers.tls.extensions import TLS_Ext_ServerName

logger = logging.getLogger(__name__)

def replay_pcap(pcap_path: str) -> Iterator[Dict[str, Any]]:
    """
    Replay a PCAP file using Scapy, aggregating packets into flows.
    Yields flow dictionaries to the detection engine.
    """
    logger.info(f"Using Scapy to strictly parse {pcap_path}")
    
    active_flows = {}
    FLOW_TIMEOUT_MS = 2000 # 2 seconds
    
    with PcapReader(pcap_path) as pcap_reader:
        for pkt in pcap_reader:
            if IP in pkt:
                proto = 6 if TCP in pkt else (17 if UDP in pkt else pkt[IP].proto)
                src_port = pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else 0)
                dst_port = pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0)
                
                pkt_time_ms = int(float(pkt.time) * 1000)
                
                # Normalize flow key (bidirectional)
                if pkt[IP].src < pkt[IP].dst:
                    flow_key = f"{pkt[IP].src}:{src_port}-{pkt[IP].dst}:{dst_port}-{proto}"
                    is_forward = True
                else:
                    flow_key = f"{pkt[IP].dst}:{dst_port}-{pkt[IP].src}:{src_port}-{proto}"
                    is_forward = False
                    
                # Check for timeouts
                expired_keys = []
                for k, f in active_flows.items():
                    if pkt_time_ms - f["bidirectional_last_seen_ms"] > FLOW_TIMEOUT_MS:
                        expired_keys.append(k)
                        
                for k in expired_keys:
                    yield active_flows.pop(k)
                
                if flow_key not in active_flows:
                    active_flows[flow_key] = {
                        "id": flow_key,
                        "src_ip": pkt[IP].src if is_forward else pkt[IP].dst,
                        "dst_ip": pkt[IP].dst if is_forward else pkt[IP].src,
                        "src_port": src_port if is_forward else dst_port,
                        "dst_port": dst_port if is_forward else src_port,
                        "protocol": proto,
                        "application_name": "UNKNOWN",
                        "bidirectional_first_seen_ms": pkt_time_ms,
                        "bidirectional_last_seen_ms": pkt_time_ms,
                        "bidirectional_duration_ms": 0,
                        "bidirectional_packets": 0,
                        "bidirectional_bytes": 0,
                        "src2dst_bytes": 0,
                        "dst2src_bytes": 0,
                        "tcp_flags": 0,
                        "dns_query": None,
                        "dns_qtype": None,
                        "tls_sni": None,
                        "tls_ja3": None
                    }
                    
                flow = active_flows[flow_key]
                flow["bidirectional_last_seen_ms"] = pkt_time_ms
                flow["bidirectional_duration_ms"] = pkt_time_ms - flow["bidirectional_first_seen_ms"]
                flow["bidirectional_packets"] += 1
                flow["bidirectional_bytes"] += len(pkt)
                
                if is_forward:
                    flow["src2dst_bytes"] += len(pkt)
                else:
                    flow["dst2src_bytes"] += len(pkt)
                    
                if TCP in pkt:
                    flow["tcp_flags"] |= int(getattr(pkt[TCP], 'flags', 0))
                    
                # DNS Passive Extraction
                if pkt.haslayer(DNS) and pkt.haslayer(DNSQR):
                    try:
                        flow["dns_query"] = pkt[DNSQR].qname.decode('utf-8').rstrip('.')
                        flow["dns_qtype"] = pkt[DNSQR].qtype
                    except Exception:
                        pass
                        
                # TLS Passive Extraction
                if pkt.haslayer(TLSClientHello):
                    ch = pkt[TLSClientHello]
                    try:
                        version = str(ch.version)
                        ciphers = "-".join([str(c) for c in ch.ciphers])
                        flow["tls_ja3"] = hashlib.md5(f"{version},{ciphers}".encode()).hexdigest()
                    except Exception:
                        pass
                        
                    if pkt.haslayer(TLS_Ext_ServerName):
                        try:
                            sn_ext = pkt[TLS_Ext_ServerName]
                            if sn_ext.servernames:
                                flow["tls_sni"] = sn_ext.servernames[0].servername.decode('utf-8')
                        except Exception:
                            pass
                            
        # Flush remaining flows at the end of PCAP
        for k, f in active_flows.items():
            yield f
