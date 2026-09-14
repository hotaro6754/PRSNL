import json
import uuid
from typing import Iterator, Dict, Any, Optional
from backend.contracts.observation import NetworkObservation
from backend.ingestion.base import BaseIngestionAdapter

class ZeekJSONAdapter(BaseIngestionAdapter):
    """
    Ingests Zeek JSON logs (conn.log, etc.) and transforms them into NetworkObservations.
    """
    def __init__(self, sensor_id: str = "zeek_sensor"):
        self.sensor_id = sensor_id

    def consume(self, filepath: str) -> Iterator[NetworkObservation]:
        """
        Reads a Zeek JSON log file (e.g. conn.log) and yields observations.
        Note: A full production adapter might subscribe to a Zeek JSON stream over a socket/named pipe.
        """
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    obs = self._map_conn_log(record)
                    if obs:
                        yield obs
                except json.JSONDecodeError:
                    continue

    def _map_conn_log(self, record: Dict[str, Any]) -> Optional[NetworkObservation]:
        """
        Maps a standard Zeek conn.log JSON record to NetworkObservation.
        """
        # Example Zeek conn.log fields:
        # ts, uid, id.orig_h, id.orig_p, id.resp_h, id.resp_p, proto, duration, orig_bytes, resp_bytes,
        # orig_pkts, resp_pkts, history, orig_state, resp_state
        
        if "id.orig_h" not in record:
            return None # Not a conn log
            
        ts_sec = float(record.get("ts", 0))
        ts_ms = int(ts_sec * 1000)
        
        duration = float(record.get("duration", 0.0))
        
        proto_str = record.get("proto", "unknown")
        proto_map = {"tcp": 6, "udp": 17, "icmp": 1}
        proto = proto_map.get(proto_str, 0)
        
        orig_bytes = int(record.get("orig_bytes", 0))
        resp_bytes = int(record.get("resp_bytes", 0))
        orig_pkts = int(record.get("orig_pkts", 0))
        resp_pkts = int(record.get("resp_pkts", 0))
        
        total_bytes = orig_bytes + resp_bytes
        total_pkts = orig_pkts + resp_pkts
        
        # Zeek uid used as flow_id
        flow_id = record.get("uid", str(uuid.uuid4()))
        
        return NetworkObservation(
            observation_id=str(uuid.uuid4()),
            timestamp=ts_ms,
            sensor_id=self.sensor_id,
            source_ip=record.get("id.orig_h", "0.0.0.0"),
            destination_ip=record.get("id.resp_h", "0.0.0.0"),
            source_port=int(record.get("id.orig_p", 0)),
            destination_port=int(record.get("id.resp_p", 0)),
            protocol=proto,
            flow_id=flow_id,
            first_seen=ts_ms,
            last_seen=ts_ms + int(duration * 1000),
            duration=duration,
            packets=total_pkts,
            bytes=total_bytes,
            src2dst_bytes=orig_bytes,
            dst2src_bytes=resp_bytes,
            bidirectional_bytes=total_bytes,
            bidirectional_packets=total_pkts,
            bidirectional_first_seen_ms=ts_ms,
            bidirectional_last_seen_ms=ts_ms + int(duration * 1000)
            # Future: join with dns.log / ssl.log by `uid` for tls_ja3, dns_query, etc.
        )
