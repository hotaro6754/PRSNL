import glob
import re

for filename in glob.glob('verify_*.py'):
    with open(filename, 'r') as f:
        content = f.read()
        
    content = content.replace(
        'from backend.replay.pcap_engine import replay_pcap',
        'from backend.ingestion.scapy_adapter import ScapyAdapter'
    )
    
    # Replace or flow in replay_pcap(pcap_file): with dapter = ScapyAdapter(); for flow in adapter.consume(pcap_file):
    # or just replace the loop
    content = re.sub(
        r'for flow in replay_pcap\((.*?)\):',
        r'adapter = ScapyAdapter()\n        for flow in adapter.consume(\1):',
        content
    )
    
    with open(filename, 'w') as f:
        f.write(content)
