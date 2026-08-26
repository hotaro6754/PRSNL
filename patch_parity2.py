import re

with open('parity_check.py', 'r') as f:
    content = f.read()

content = content.replace("print('Could not generate features for one or both.')", "print(f'Scapy: {bool(scapy_f)}, Zeek: {bool(zeek_f)}')")

with open('parity_check.py', 'w') as f:
    f.write(content)
