"""
Patch docker-compose.yml to mount Grafana provisioning.
"""
import re

with open('docker-compose.yml', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(grafana:\n.*?volumes:\n.*?-\s*grafana_data:/var/lib/grafana)'
match = re.search(pattern, content, re.DOTALL)
if match:
    old_volumes = match.group(1)
    new_volumes = old_volumes + "\n    - ./grafana/provisioning:/etc/grafana/provisioning\n    - ./grafana/dashboards:/etc/grafana/provisioning/dashboards"
    content = content.replace(old_volumes, new_volumes)
    with open('docker-compose.yml', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched docker-compose.yml for Grafana provisioning.")
else:
    print("Could not find grafana volumes block!")
