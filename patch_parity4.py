import re

with open('parity_check.py', 'r') as f:
    content = f.read()

new_parse = '''    from backend.streaming.zeek_adapter import ZeekTailer
    tailer = ZeekTailer([], None)
    
    flows = []
    if os.path.exists(conn_log):
        with open(conn_log, 'r') as f:
            for line in f:
                try:
                    flow = tailer._parse_zeek_json(line)
                    flows.append(flow)
                except Exception as e:
                    pass'''

content = re.sub(r"    from backend\.contracts\.observation import NetworkObservation\n    \n    flows = \[\]\n    if os\.path\.exists\(conn_log\):\n        with open\(conn_log, 'r'\) as f:\n            for line in f:\n                try:\n                    data = json\.loads\(line\).*?except Exception as e:\n                    import traceback\n                    traceback\.print_exc\(\)", new_parse, content, flags=re.DOTALL)

with open('parity_check.py', 'w') as f:
    f.write(content)
