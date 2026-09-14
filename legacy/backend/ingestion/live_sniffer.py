import logging
import threading
import time
import uuid
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)

class LiveNetworkSniffer:
    """
    Passive Line-Rate Live Network Interface Sniffer for NTRO Sentinel-26145.
    Passively taps incoming simplex/unidirectional IP frames on any network interface.
    Extracts directional flow counters and dispatches NetworkObservation records.
    """
    def __init__(self, callback: Optional[Callable[[Any], Any]] = None):
        self.callback = callback
        self._sniffer = None
        self._is_running = False
        self.interface = None
        self.active_flows: Dict[tuple, dict] = {}
        self.total_packets_sniffed = 0
        self.total_bytes_sniffed = 0
        self.start_time = 0.0

    @property
    def is_running(self) -> bool:
        return self._is_running and self._sniffer is not None and getattr(self._sniffer, "running", False)

    def start(self, interface: Optional[str] = None, bpf_filter: str = "ip"):
        try:
            from scapy.all import AsyncSniffer, conf
        except ImportError:
            logger.error("Scapy is not installed. Live sniffing disabled.")
            return {"status": "error", "message": "Scapy not installed"}

        if self.is_running:
            logger.warning("Sniffer already running on %s", self.interface)
            return {"status": "already_running", "interface": str(self.interface)}

        self.interface = interface or conf.iface
        self._is_running = True
        self.start_time = time.time()
        self.total_packets_sniffed = 0
        self.total_bytes_sniffed = 0
        self.active_flows.clear()

        try:
            self._sniffer = AsyncSniffer(
                iface=self.interface,
                filter=bpf_filter,
                prn=self._handle_packet,
                store=False
            )
            self._sniffer.start()
            logger.info("Live network sniffer started on interface: %s with filter: %s", self.interface, bpf_filter)
            return {"status": "started", "interface": str(self.interface), "filter": bpf_filter}
        except Exception as e:
            self._is_running = False
            logger.error("Failed to start sniffer on %s: %s", self.interface, e)
            return {"status": "error", "message": str(e), "interface": str(self.interface)}

    def stop(self):
        if not self._is_running:
            return {"status": "not_running"}
        try:
            if self._sniffer and getattr(self._sniffer, "running", False):
                self._sniffer.stop()
            self._is_running = False
            for f in list(self.active_flows.values()):
                if self.callback:
                    self.callback(self._to_observation(f))
            self.active_flows.clear()
            logger.info("Live network sniffer stopped on %s", self.interface)
            return {
                "status": "stopped",
                "packets_captured": self.total_packets_sniffed,
                "bytes_captured": self.total_bytes_sniffed
            }
        except Exception as e:
            logger.error("Error stopping sniffer: %s", e)
            return {"status": "error", "message": str(e)}

    def get_stats(self) -> dict:
        uptime = round(time.time() - self.start_time, 1) if self._is_running else 0.0
        return {
            "is_running": self.is_running,
            "interface": str(self.interface),
            "packets_captured": self.total_packets_sniffed,
            "bytes_captured": self.total_bytes_sniffed,
            "active_flows_tracked": len(self.active_flows),
            "uptime_seconds": uptime
        }

    def _handle_packet(self, pkt):
        from scapy.all import IP, TCP, UDP, ICMP
        if not IP in pkt:
            return

        self.total_packets_sniffed += 1
        pkt_len = len(pkt)
        self.total_bytes_sniffed += pkt_len

        proto = 6 if TCP in pkt else (17 if UDP in pkt else (1 if ICMP in pkt else pkt[IP].proto))
        src_port = pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else 0)
        dst_port = pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0)
        pkt_time_ms = int(time.time() * 1000)

        ip_src = pkt[IP].src
        ip_dst = pkt[IP].dst

        key = (ip_src, src_port, ip_dst, dst_port, proto)

        if key not in self.active_flows:
            self.active_flows[key] = {
                "id": str(uuid.uuid4()),
                "first_seen": pkt_time_ms,
                "last_seen": pkt_time_ms,
                "proto": proto,
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
                "dns_query": None,
                "tls_sni": None
            }

        f = self.active_flows[key]
        f["last_seen"] = pkt_time_ms
        f["orig_packets"] += 1
        f["orig_ip_bytes"] += pkt_len

        if TCP in pkt:
            flags = pkt[TCP].flags
            if 'S' in flags: f["syn_orig"] = True
            if 'F' in flags: f["fin_orig"] = True
            if 'R' in flags: f["rst_orig"] = True

        if UDP in pkt and (src_port == 53 or dst_port == 53):
            try:
                from scapy.all import DNS, DNSQR
                if DNS in pkt and pkt[DNS].qd:
                    f["dns_query"] = pkt[DNS][DNSQR].qname.decode('utf-8', errors='ignore').rstrip('.')
            except Exception:
                pass

        if f["orig_packets"] >= 10 or (pkt_time_ms - f["first_seen"]) >= 2000:
            obs = self._to_observation(f)
            if self.callback:
                self.callback(obs)
            f["first_seen"] = pkt_time_ms
            f["orig_packets"] = 0
            f["orig_ip_bytes"] = 0

    def _to_observation(self, flow: dict):
        from backend.contracts.observation import NetworkObservation
        return NetworkObservation(
            observation_id=flow["id"],
            timestamp=flow["first_seen"],
            capture_id="live_tap",
            source_ip=flow["orig_ip"],
            destination_ip=flow["resp_ip"],
            source_port=flow["orig_port"],
            destination_port=flow["resp_port"],
            protocol=flow["proto"],
            flow_id=flow["id"],
            first_seen=flow["first_seen"],
            last_seen=flow["last_seen"],
            duration=max(0.0, float(flow["last_seen"] - flow["first_seen"])),
            orig_packets=max(1, flow["orig_packets"]),
            resp_packets=0,
            orig_ip_bytes=max(40, flow["orig_ip_bytes"]),
            resp_ip_bytes=0,
            tcp_syn_orig=flow["syn_orig"],
            tcp_syn_resp=False,
            tcp_fin_orig=flow["fin_orig"],
            tcp_fin_resp=False,
            tcp_rst_orig=flow["rst_orig"],
            tcp_rst_resp=False,
            dns_query=flow.get("dns_query"),
            tls_sni=flow.get("tls_sni"),
            tls_ja3=None
        )
