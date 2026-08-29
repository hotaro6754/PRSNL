import re
with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add it after "import os"
content = content.replace("import os", "import os\nfrom collections import deque\nrecent_flows_buffer = deque(maxlen=100)\n")

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
