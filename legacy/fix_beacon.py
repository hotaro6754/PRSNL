import re

with open('backend/detectors/beacon.py', 'r') as f:
    content = f.read()

# I need to change evaluate_window so it processes the flows and garbage collects.
new_eval = '''    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        alerts = []
        for flow in flows:
            src = flow.source_ip
            dst = flow.destination_ip
            port = flow.destination_port
            proto = flow.protocol
            ts = flow.timestamp
            b_bytes = flow.bidirectional_bytes or 0
            
            if src and dst and ts:
                key = (src, dst, port, proto)
                if key not in self.state:
                    self.state[key] = {
                        "timestamps": deque(maxlen=self.max_history),
                        "bytes": deque(maxlen=self.max_history),
                        "last_seen": ts,
                        "alerted": False
                    }
                
                if not self.state[key]["timestamps"] or self.state[key]["timestamps"][-1] != ts:
                    self.state[key]["timestamps"].append(ts)
                    self.state[key]["bytes"].append(b_bytes)
                    self.state[key]["last_seen"] = ts
                    
                    if not self.state[key]["alerted"] and len(self.state[key]["timestamps"]) >= self.min_flows_required:
                        alert = self._evaluate_stream(key, self.state[key], flow)
                        if alert:
                            alerts.append(alert)
                            self.state[key]["alerted"] = True
                            
        self._garbage_collect(window_start_ms)
        return alerts
'''

# Let's replace the existing evaluate_window
content = re.sub(r'    def evaluate_window\(self, flows: List\[NetworkObservation\], window_start_ms: int\) -> List\[Alert\]:.*?return \[\]', new_eval, content, flags=re.DOTALL)

with open('backend/detectors/beacon.py', 'w') as f:
    f.write(content)
