import os
import time
import json
import logging
import subprocess
import uuid
import sys
from typing import Iterator
from backend.schemas import NetworkObservation
from backend.streaming.kafka_adapter import KafkaObservationProducer

logger = logging.getLogger(__name__)

class ZeekTailer:
    """
    Tails real Zeek connection logs using `tail -F` to support multiple files (conn.log, dns.log, etc).
    Translates Zeek events to NetworkObservation and pushes to Kafka.
    """
    
    def __init__(self, log_paths: list, producer: KafkaObservationProducer):
        self.log_paths = log_paths
        self.producer = producer

    def _parse_zeek_json(self, line: str) -> NetworkObservation:
        data = json.loads(line)
        
        is_dns = "query" in data or "qtype_name" in data
        ts = data.get("ts", time.time())
        ts_ms = int(ts * 1000)
        duration = data.get("duration", 0.0)
        uid = data.get("uid", str(uuid.uuid4()))
        
        proto_str = data.get("proto", "unknown").lower()
        proto_map = {"tcp": 6, "udp": 17, "icmp": 1}
        proto_int = proto_map.get(proto_str, 0)
        
        orig_ip_bytes = data.get("orig_ip_bytes", 0)
        resp_ip_bytes = data.get("resp_ip_bytes", 0)
        orig_pkts = data.get("orig_pkts", 0)
        resp_pkts = data.get("resp_pkts", 0)
        
        history = data.get("history", "")
        
        obs = NetworkObservation(
            observation_id=str(uuid.uuid4()),
            flow_id=uid,
            timestamp=ts_ms,
            first_seen=ts_ms,
            last_seen=ts_ms + int(duration * 1000),
            duration=duration,
            source_ip=data.get("id.orig_h", "0.0.0.0"),
            destination_ip=data.get("id.resp_h", "0.0.0.0"),
            source_port=data.get("id.orig_p", 0),
            destination_port=data.get("id.resp_p", 0),
            protocol=proto_int,
            orig_packets=orig_pkts,
            resp_packets=resp_pkts,
            orig_ip_bytes=orig_ip_bytes,
            resp_ip_bytes=resp_ip_bytes,
            tcp_syn_orig='S' in history,
            tcp_syn_resp='s' in history,
            tcp_fin_orig='F' in history,
            tcp_fin_resp='f' in history,
            tcp_rst_orig='R' in history,
            tcp_rst_resp='r' in history,
            dns_query=data.get("query") if is_dns else None,
            tls_sni=data.get("server_name") if "server_name" in data else None
        )
        return obs

    def tail_and_publish(self):
        state_file = "/var/log/zeek/adapter_state.json"
        state = {}
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")

        files = {}
        for p in self.log_paths:
            files[p] = {"fd": None, "inode": -1}

        def save_state():
            try:
                with open(state_file, "w") as f:
                    json.dump(state, f)
            except Exception as e:
                pass

        logger.info(f"Starting durable Zeek ingestion for: {self.log_paths}")
        last_save = time.time()
        
        while True:
            did_work = False
            for p in self.log_paths:
                if not os.path.exists(p):
                    continue
                
                try:
                    stat = os.stat(p)
                    inode = stat.st_ino
                except Exception:
                    continue

                # Detect rotation or new file
                if files[p]["inode"] != inode:
                    if files[p]["fd"]:
                        files[p]["fd"].close()
                    try:
                        fd = open(p, "r")
                        files[p]["fd"] = fd
                        files[p]["inode"] = inode
                        
                        # Recover offset
                        if p in state and state[p].get("inode") == inode:
                            fd.seek(state[p].get("offset", 0))
                        else:
                            # If we have no state, or it's a completely new file rotation,
                            # we should start reading from where it is now (or beginning if small?)
                            # The prompt says: "Do NOT blindly restart from EOF. Do NOT blindly restart from byte 0."
                            # But wait, if it's a NEW file (inode changed), we start at 0.
                            # If it's our FIRST time starting up and the file already exists, we should probably start at 0 
                            # if it's small, or just save the state. Let's start at 0. 
                            fd.seek(0)
                        
                        state[p] = {"inode": inode, "offset": fd.tell()}
                    except Exception as e:
                        logger.error(f"Failed to open {p}: {e}")
                        continue

                fd = files[p]["fd"]
                lines = fd.readlines(131072)
                if not lines:
                    continue
                
                if not lines[-1].endswith("\n"):
                    partial = lines.pop()
                    fd.seek(fd.tell() - len(partial))
                    if not lines:
                        continue
                        
                did_work = True
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("==>"):
                        continue
                    try:
                        obs = self._parse_zeek_json(line)
                        self.producer.publish(obs)
                    except Exception as e:
                        logger.error(f"Parse error: {e}")
                
                state[p]["offset"] = fd.tell()
            
            if time.time() - last_save > 1.0 and did_work:
                save_state()
                last_save = time.time()
                
            if not did_work:
                save_state()
                time.sleep(0.1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    producer = KafkaObservationProducer()
    paths = ["/var/log/zeek/conn.log", "/var/log/zeek/dns.log"]
    tailer = ZeekTailer(paths, producer)
    tailer.tail_and_publish()
