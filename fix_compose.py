import re
with open('docker-compose.yml', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'\s*-\s*\./grafana/dashboards:/etc/grafana/provisioning/dashboards\n', '\n', content)

with open('docker-compose.yml', 'w', encoding='utf-8') as f:
    f.write(content)
print("Removed offending mount")
