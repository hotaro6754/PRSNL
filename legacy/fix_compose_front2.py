import yaml

with open('docker-compose.yml', 'r') as f:
    data = yaml.safe_load(f)

if 'frontend' in data['services']:
    data['services']['frontend']['command'] = ['npm', 'start']

with open('docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
