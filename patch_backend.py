import yaml

with open('docker-compose.prod.yml', 'r') as f:
    data = yaml.safe_load(f)

for service in ['backend', 'ml_worker', 'zeek_adapter']:
    if 'volumes' not in data['services'][service]:
        data['services'][service]['volumes'] = []
    
    # Remove old bind mounts if exist
    data['services'][service]['volumes'] = [v for v in data['services'][service]['volumes'] if not v.startswith('./backend') and not v.startswith('./models')]
    
    # Add bind mounts
    data['services'][service]['volumes'].append('./backend:/app/backend:ro')
    data['services'][service]['volumes'].append('./models:/app/models:ro')

with open('docker-compose.prod.yml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
