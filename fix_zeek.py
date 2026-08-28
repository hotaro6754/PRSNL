import re
with open('backend/streaming/zeek_adapter.py', 'r') as f:
    code = f.read()

code = code.replace(
    "line = line.strip(); if not line or line.startswith('#'): return None; data = json.loads(line)",
    "line = line.strip()\n        if not line or line.startswith('#'):\n            return None\n        data = json.loads(line)"
)

with open('backend/streaming/zeek_adapter.py', 'w') as f:
    f.write(code)
