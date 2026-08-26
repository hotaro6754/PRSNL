import yaml

with open('docker-compose.prod.yml', 'r') as f:
    data = yaml.safe_load(f)

if 'command' in data['services']['redpanda']:
    data['services']['redpanda']['command'] = [c.replace('2G', '512M') if '2G' in c else c for c in data['services']['redpanda']['command']]

if 'frontend' in data['services']:
    del data['services']['frontend']

with open('docker-compose.prod.yml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
