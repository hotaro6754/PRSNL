from pydantic import BaseModel, Field
from typing import Optional

class NetworkObservation(BaseModel):
    organization_id: str = "default_org"
    """
    The canonical data contract for passive network telemetry.
    Detectors consume this regardless of ingestion source (Scapy, Zeek, etc.).
    """
    observation_id: str
    timestamp: int  # event_time ms
    sensor_id: str = "default_sensor"
    
    # Connection Identity & Direction (Originator is ALWAYS source)
    source_ip: str  # Originator IP
    destination_ip: str  # Responder IP
    source_port: int
    destination_port: int
    protocol: int  # IANA protocol number (6=TCP, 17=UDP, 1=ICMP)
    
    # Timing
    flow_id: str
    first_seen: int  # ms
    last_seen: int  # ms
    duration: float  # ms
    
    # Flow Volume (Canonical IP bytes)
    orig_packets: int
    resp_packets: int
    orig_ip_bytes: int
    resp_ip_bytes: int
    
    # Protocol Metadata
    tcp_syn_orig: bool = False
    tcp_syn_resp: bool = False
    tcp_fin_orig: bool = False
    tcp_fin_resp: bool = False
    tcp_rst_orig: bool = False
    tcp_rst_resp: bool = False
    
    dns_query: Optional[str] = None
    tls_sni: Optional[str] = None
    tls_ja3: Optional[str] = None
    
    @property
    def packets(self): return self.orig_packets + self.resp_packets
    
    @property
    def bidirectional_bytes(self): return self.orig_ip_bytes + self.resp_ip_bytes
    
    @property
    def src2dst_bytes(self): return self.orig_ip_bytes
    
    @property
    def dst2src_bytes(self): return self.resp_ip_bytes
