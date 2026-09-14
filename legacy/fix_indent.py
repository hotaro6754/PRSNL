import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The second occurrence inside get_ml_metrics:
bad_block = """    import json
    import os
from collections import deque
recent_flows_buffer = deque(maxlen=100)"""

good_block = """    import json
    import os"""

content = content.replace(bad_block, good_block)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed indentation error")
