import yaml

with open('docker-compose.prod.yml', 'r') as f:
    data = yaml.safe_load(f)

if 'volumes' not in data['services']['backend']:
    data['services']['backend']['volumes'] = []
data['services']['backend']['volumes'].append('./models:/app/models:ro')

if 'volumes' not in data['services']['ml_worker']:
    data['services']['ml_worker']['volumes'] = []
data['services']['ml_worker']['volumes'].append('./models:/app/models:ro')

with open('docker-compose.prod.yml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
