import re

with open('backend/ml/router.py', 'r') as f:
    content = f.read()

content = content.replace('self.stage = "SHADOW"', 'self.stage = "EVALUATION"')

with open('backend/ml/router.py', 'w') as f:
    f.write(content)
