import os
import sys
import subprocess
import json

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.ingestion.scapy_adapter import ScapyAdapter
from backend.ml.feature_engine import TumblingWindowFeatureEngine

def get_scapy_features(pcap_file):
    print(f'[*] Running ScapyAdapter on {pcap_file}')
    adapter = ScapyAdapter(flow_timeout_ms=10000)
    flows = list(adapter.consume(pcap_file))
    flows.sort(key=lambda x: x.timestamp)
    engine = TumblingWindowFeatureEngine()
    if flows:
        return engine.extract_features(flows).model_dump()
    return None

def get_zeek_features(pcap_file):
    print(f'[*] Running Zeek on {pcap_file}')
    out_dir = 'zeek_logs_parity'
    os.makedirs(out_dir, exist_ok=True)
    # We copy the pcap to the zeek container, run zeek, and copy the logs back
    subprocess.run(['docker', 'cp', os.path.abspath(pcap_file), 'sih26145-zeek-prod:/tmp/parity.pcap'], check=True)
    subprocess.run(['docker', 'exec', 'sih26145-zeek-prod', 'mkdir', '-p', '/tmp/zeek_logs_parity'], check=True)
    subprocess.run(['docker', 'exec', 'sih26145-zeek-prod', 'sh', '-c', 'cd /tmp/zeek_logs_parity && zeek -r /tmp/parity.pcap local LogAscii::use_json=T'], check=True)
    subprocess.run(['docker', 'cp', 'sih26145-zeek-prod:/tmp/zeek_logs_parity/conn.log', os.path.join(out_dir, 'conn.log')], check=True)
    
    conn_log = os.path.join(out_dir, 'conn.log')
    from backend.streaming.zeek_adapter import ZeekTailer
    tailer = ZeekTailer([], None)
    
    flows = []
    if os.path.exists(conn_log):
        with open(conn_log, 'r') as f:
            for line in f:
                try:
                    flow = tailer._parse_zeek_json(line)
                    flows.append(flow)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    
    flows.sort(key=lambda x: x.timestamp)
    engine = TumblingWindowFeatureEngine()
    if flows:
        return engine.extract_features(flows).model_dump()
    return None
    
