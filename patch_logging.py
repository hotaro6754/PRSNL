"""
Patch backend/main.py to redirect uvicorn logs to logs/backend.log
"""
import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(logging\.basicConfig\(\n.*?level=logging\.INFO,\n.*?format="%\(asctime\)s \[%\(levelname\)s\] %\(name\)s: %\(message\)s",\n.*?handlers=\[\n.*?RotatingFileHandler\("logs/backend\.log", maxBytes=5000000, backupCount=2\),\n.*?logging\.StreamHandler\(\)\n.*?\]\n\))'
match = re.search(pattern, content, re.DOTALL)
if match:
    old_log = match.group(1)
    
    new_log = old_log + "\n" + """
for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
    ulogger = logging.getLogger(logger_name)
    ulogger.setLevel(logging.INFO)
    for handler in ulogger.handlers[:]:
        ulogger.removeHandler(handler)
    ulogger.addHandler(RotatingFileHandler("logs/backend.log", maxBytes=5000000, backupCount=2))
    ulogger.addHandler(logging.StreamHandler())
"""
    content = content.replace(old_log, new_log)
    with open('backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched backend/main.py to capture uvicorn logs.")
else:
    print("Could not find logging.basicConfig block!")
