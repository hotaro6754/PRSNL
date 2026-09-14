import re

with open('backend/detectors/dns_tunnel.py', 'r') as f:
    content = f.read()

new_eval = '''    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        alerts = []
        for flow in flows:
            domain = flow.dns_query
            src = flow.source_ip
            ts = flow.timestamp
            
            if src and domain and ts:
                root_domain = self.get_root_domain(domain)
                key = (src, root_domain)
                
                if key not in self.state:
                    self.state[key] = {
                        "unique_subdomains": set(),
                        "total_payload_bytes": 0,
                        "last_seen": ts,
                        "alerted": False,
                        "query_count": 0
                    }
                    
                stream = self.state[key]
                stream["last_seen"] = ts
                stream["query_count"] += 1
                
                subdomain = domain[:-(len(root_domain)+1)] if domain.endswith(f".{root_domain}") else ""
                
                if subdomain and subdomain not in stream["unique_subdomains"]:
                    if len(stream["unique_subdomains"]) < self.max_unique_subdomains + 10:
                        stream["unique_subdomains"].add(subdomain)
                        stream["total_payload_bytes"] += len(subdomain)
                        
                if not stream["alerted"] and len(stream["unique_subdomains"]) >= self.max_unique_subdomains:
                    if stream["total_payload_bytes"] >= self.min_payload_bytes:
                        alert = self._generate_alert(key, stream, flow)
                        alerts.append(alert)
                        stream["alerted"] = True
                        
        self._garbage_collect(window_start_ms)
        return alerts
'''

content = re.sub(r'    def evaluate_window\(self, flows: List\[NetworkObservation\], window_start_ms: int\) -> List\[Alert\]:.*?return \[\]', new_eval, content, flags=re.DOTALL)

with open('backend/detectors/dns_tunnel.py', 'w') as f:
    f.write(content)
