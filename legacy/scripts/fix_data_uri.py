import re

with open('backend/content/web_analyzer.py', 'r') as f:
    code = f.read()

replacement = """
def resolve_and_check_ssrf(url: str):
    if url.startswith("data:"):
        return True
    
    parsed = urlparse(url)
    hostname = parsed.hostname
"""

code = code.replace("def resolve_and_check_ssrf(url: str):\n    parsed = urlparse(url)\n    hostname = parsed.hostname", replacement)

with open('backend/content/web_analyzer.py', 'w') as f:
    f.write(code)
print("Updated web_analyzer.py to support data URIs for isolated LAB testing")
