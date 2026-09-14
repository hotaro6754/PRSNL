import re

with open('backend/streaming/zeek_adapter.py', 'r') as f:
    content = f.read()

new_parse = '''    def _parse_zeek_json(self, line: str) -> NetworkObservation:
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
        return obs'''

content = re.sub(r'    def _parse_zeek_json\(self, line: str\) -> NetworkObservation:.*?(?=    def tail_and_publish\(self\):)', new_parse + '\n\n', content, flags=re.DOTALL)

with open('backend/streaming/zeek_adapter.py', 'w') as f:
    f.write(content)
