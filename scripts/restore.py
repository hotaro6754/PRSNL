import re

with open('backend/main.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "from fastapi.responses import HTMLResponse" in line:
        skip = True
    if skip and '    \"\"\"' in line and '</html>' not in line and '</body>' not in line: 
        # Extremely bad way to parse, let's just restore original then inject safely at EOF.
        pass

