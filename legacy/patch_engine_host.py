import re

with open('backend/ml/feature_engine.py', 'r') as f:
    content = f.read()

content = content.replace("profile = self.host_manager.get_features(host_ip)", "profile = self.host_manager.get_features(host_ip, last_ts)")

with open('backend/ml/feature_engine.py', 'w') as f:
    f.write(content)
