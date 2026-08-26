import logging
from typing import Iterator, Dict, Any, Tuple
import time
import uuid

from scapy.all import PcapReader, IP, TCP, UDP, ICMP
from backend.ingestion.base import BaseIngestionAdapter
from backend.contracts.observation import NetworkObservation

logger = logging.getLogger(__name__)

class ScapyAdapter(BaseIngestionAdapter):
    def __init__(self, flow_timeout_ms: int = 10000):
        self.flow_timeout_ms = flow_timeout_ms
        
    def consume(self, source: str) -> Iterator[NetworkObservation]:
        logger.info(f"Using ScapyAdapter to strictly parse {source}")
        
        # Key: (ipA, portA, ipB, portB, proto) always sorted lexically for state tracking
        # We will determine canonical direction internally.
        active_flows = {}
        
        with PcapReader(source) as pcap_reader:
            for pkt in pcap_reader:
                if IP in pkt:
                    proto = 6 if TCP in pkt else (17 if UDP in pkt else (1 if ICMP in pkt else pkt[IP].proto))
                    src_port = pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else 0)
                    dst_port = pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0)
                    
                    pkt_time_ms = int(float(pkt.time) * 1000)
                    
                    ip_src = pkt[IP].src
                    ip_dst = pkt[IP].dst
                    
                    # IP packet length (total length) - equivalent to Zeek's orig_ip_bytes
                    ip_len = pkt[IP].len
                    
                    # Connection key for state grouping
                    if ip_src < ip_dst:
                        key = (ip_src, src_port, ip_dst, dst_port, proto)
                    else:
                        key = (ip_dst, dst_port, ip_src, src_port, proto)
                        
                    if key not in active_flows:
                        active_flows[key] = {
                            "id": str(uuid.uuid4()),
                            "first_seen": pkt_time_ms,
                            "last_seen": pkt_time_ms,
                            "proto": proto,
                            # We lock the originator to the first packet seen!
                            "orig_ip": ip_src,
                            "resp_ip": ip_dst,
                            "orig_port": src_port,
                            "resp_port": dst_port,
                            "orig_packets": 0,
                            "resp_packets": 0,
                            "orig_ip_bytes": 0,
                            "resp_ip_bytes": 0,
                            "syn_orig": False,
                            "syn_resp": False,
                            "fin_orig": False,
                            "fin_resp": False,
                            "rst_orig": False,
                            "rst_resp": False,
                        }
                        
                    f = active_flows[key]
                    f["last_seen"] = pkt_time_ms
                    
                    is_orig = (ip_src == f["orig_ip"])
                    
                    if is_orig:
                        f["orig_packets"] += 1
                        f["orig_ip_bytes"] += ip_len
                    else:
                        f["resp_packets"] += 1
                        f["resp_ip_bytes"] += ip_len
                        
                    if TCP in pkt:
                        flags = pkt[TCP].flags
                        if 'S' in flags:
                            if is_orig: f["syn_orig"] = True
                            else: f["syn_resp"] = True
                        if 'F' in flags:
                            if is_orig: f["fin_orig"] = True
                            else: f["fin_resp"] = True
                        if 'R' in flags:
                            if is_orig: f["rst_orig"] = True
                            else: f["rst_resp"] = True

            # Flush remaining
            for f in active_flows.values():
                yield self._to_observation(f)

    def _to_observation(self, flow: dict) -> NetworkObservation:
        return NetworkObservation(
            observation_id=flow["id"],
            timestamp=flow["first_seen"],
            capture_id="offline_pcap",
            source_ip=flow["orig_ip"],
            destination_ip=flow["resp_ip"],
            source_port=flow["orig_port"],
            destination_port=flow["resp_port"],
            protocol=flow["proto"],
            flow_id=flow["id"],
            first_seen=flow["first_seen"],
            last_seen=flow["last_seen"],
            duration=max(0.0, flow["last_seen"] - flow["first_seen"]),
            orig_packets=flow["orig_packets"],
            resp_packets=flow["resp_packets"],
            orig_ip_bytes=flow["orig_ip_bytes"],
            resp_ip_bytes=flow["resp_ip_bytes"],
            tcp_syn_orig=flow["syn_orig"],
            tcp_syn_resp=flow["syn_resp"],
            tcp_fin_orig=flow["fin_orig"],
            tcp_fin_resp=flow["fin_resp"],
            tcp_rst_orig=flow["rst_orig"],
            tcp_rst_resp=flow["rst_resp"],
            dns_query=None,
            tls_sni=None,
            tls_ja3=None
        )
