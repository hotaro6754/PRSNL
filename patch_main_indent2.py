lines = []
with open('backend/main.py', 'r') as f:
    for i, line in enumerate(f):
        if 'redis_host_manager.add_flow(flow)' in line:
            if i > 225: # inside process_pcap_background
                lines.append('            redis_host_manager.add_flow(flow)\n')
            else: # inside _process_flow
                lines.append('    redis_host_manager.add_flow(flow)\n')
        else:
            lines.append(line)

with open('backend/main.py', 'w') as f:
    f.writelines(lines)
