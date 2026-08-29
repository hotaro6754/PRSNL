with open('train_window_v2.py', 'r') as f:
    content = f.read()

if 'import json' not in content:
    content = 'import json\n' + content

with open('train_window_v2.py', 'w') as f:
    f.write(content)
