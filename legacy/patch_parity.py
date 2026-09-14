import re

with open('parity_check.py', 'r') as f:
    content = f.read()

new_subprocess = '''    out_dir = 'zeek_logs_parity'
    os.makedirs(out_dir, exist_ok=True)
    # We copy the pcap to the zeek container, run zeek, and copy the logs back
    subprocess.run(['docker', 'cp', os.path.abspath(pcap_file), 'cyberos-zeek-prod:/tmp/parity.pcap'], check=True)
    subprocess.run(['docker', 'exec', 'cyberos-zeek-prod', 'mkdir', '-p', '/tmp/zeek_logs_parity'], check=True)
    subprocess.run(['docker', 'exec', 'cyberos-zeek-prod', 'sh', '-c', 'cd /tmp/zeek_logs_parity && zeek -r /tmp/parity.pcap local LogAscii::use_json=T'], check=True)
    subprocess.run(['docker', 'cp', 'cyberos-zeek-prod:/tmp/zeek_logs_parity/conn.log', os.path.join(out_dir, 'conn.log')], check=True)'''

content = re.sub(r"    out_dir = 'zeek_logs_parity'\n    os\.makedirs\(out_dir, exist_ok=True\)\n    subprocess\.run\(\['zeek', '-r', os\.path\.abspath\(pcap_file\), 'local', 'LogAscii::use_json=T'\], cwd=out_dir, check=True\)", new_subprocess, content)

with open('parity_check.py', 'w') as f:
    f.write(content)
