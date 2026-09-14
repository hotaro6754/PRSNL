import sys

with open('backend/main.py', 'r') as f:
    code = f.read()

# Replace the literal backslash-n written by powershell
code = code.replace('\\n', '\n')

with open('backend/main.py', 'w') as f:
    f.write(code)

with open('backend/content/qr_analyzer.py', 'r') as f:
    code = f.read()

code = code.replace('def analyze_qr(', 'def analyze_qr_code(')

with open('backend/content/qr_analyzer.py', 'w') as f:
    f.write(code)
