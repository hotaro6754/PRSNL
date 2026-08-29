import re

def patch_window_manager():
    with open('backend/streaming/window_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Change keys
    content = content.replace('self.windows: Dict[tuple, List[NetworkObservation]] = defaultdict(list) # Keyed by (window_id, source_ip)',
                              'self.windows: Dict[tuple, List[NetworkObservation]] = defaultdict(list)')
                              
    content = content.replace('self.windows[(wid, obs.source_ip)].append(obs)',
                              'self.windows[(wid, obs.source_ip, getattr(obs, "organization_id", "default_org"))].append(obs)')

    content = content.replace('wid, src_ip = key', 'wid, src_ip, org_id = key')
    content = content.replace('ready.append((wid, src_ip, self.windows[key]))',
                              'ready.append((wid, src_ip, org_id, self.windows[key]))')

    with open('backend/streaming/window_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
patch_window_manager()
print("Window Manager patched!")
