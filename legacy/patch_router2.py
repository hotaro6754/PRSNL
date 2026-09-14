import re

with open('backend/ml/router.py', 'r') as f:
    content = f.read()

content = content.replace('iforest_window_v2_shadow.pkl', 'iforest_host_v2.pkl')

with open('backend/ml/router.py', 'w') as f:
    f.write(content)
