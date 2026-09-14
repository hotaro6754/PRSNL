import re

with open('backend/main.py', 'r') as f:
    content = f.read()

content = content.replace('    redis_host_manager.add_flow(flow)', '            redis_host_manager.add_flow(flow)')

with open('backend/main.py', 'w') as f:
    f.write(content)
