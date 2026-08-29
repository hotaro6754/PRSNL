import re

with open('backend/detectors/tls.py', 'r') as f:
    content = f.read()

new_eval = '''    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        alerts = []
        for flow in flows:
            src = flow.source_ip
            dst = flow.destination_ip
            port = flow.destination_port
            proto = flow.protocol
            ts = flow.timestamp
            
            tls_ja3 = flow.tls_ja3
            tls_sni = flow.tls_sni
            packet_size = flow.bidirectional_bytes or 0
            
            if not src or not dst or not ts:
                continue
                
            if port not in [443, 8443, 853] and not tls_ja3:
                continue
                
            key = (src, dst, port)
            
            if key not in self.state:
                self.state[key] = {
                    "packet_sizes": deque(maxlen=20),
                    "timestamps": deque(maxlen=20),
                    "ja3_hashes": set(),
                    "snis": set(),
                    "total_bytes_out": 0,
                    "total_bytes_in": 0,
                    "last_seen": ts,
                    "alerted": False
                }
                
            stream = self.state[key]
            stream["last_seen"] = ts
            stream["packet_sizes"].append(packet_size)
            stream["timestamps"].append(ts)
            
            if tls_ja3:
                stream["ja3_hashes"].add(tls_ja3)
            if tls_sni:
                stream["snis"].add(tls_sni)
                
            if len(stream["packet_sizes"]) >= 10 and not stream["alerted"]:
                alerts.extend(self._evaluate_stream(key, stream, flow))
                
        self._garbage_collect(window_start_ms)
        return alerts
'''

content = re.sub(r'    def evaluate_window\(self, flows: List\[NetworkObservation\], window_start_ms: int\) -> List\[Alert\]:.*?return \[\]', new_eval, content, flags=re.DOTALL)

with open('backend/detectors/tls.py', 'w') as f:
    f.write(content)
