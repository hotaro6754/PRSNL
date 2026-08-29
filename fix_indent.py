import glob
import re

for filename in glob.glob('verify_*.py'):
    with open(filename, 'r') as f:
        content = f.read()
        
    content = re.sub(
        r'([ \t]+)adapter = ScapyAdapter\(\)\n[ \t]+for flow in adapter.consume\((.*?)\):',
        r'\1adapter = ScapyAdapter()\n\1for flow in adapter.consume(\2):',
        content
    )
    with open(filename, 'w') as f:
        f.write(content)
