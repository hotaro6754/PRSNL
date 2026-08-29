import re

with open('backend/ml/router.py', 'r') as f:
    content = f.read()

content = content.replace('xgb_window_v2_shadow.pkl', 'xgb_window_v4.pkl')
content = content.replace('xgb_window_v2_metadata.json', 'xgb_window_v4_metadata.json')

content = content.replace('iforest_host_v2_shadow.pkl', 'iforest_host_v2.pkl')
content = content.replace('iforest_host_v2_metadata.json', 'iforest_host_v2_metadata.json')

# There might also be window_v2 in router.py for iforest
content = content.replace('iforest_window_v2.pkl', 'iforest_host_v2.pkl')
content = content.replace('iforest_window_v2_metadata.json', 'iforest_host_v2_metadata.json')

with open('backend/ml/router.py', 'w') as f:
    f.write(content)
