import yaml

with open('docker-compose.prod.yml', 'r') as f:
    data = yaml.safe_load(f)

data['services']['redis'] = {
    'image': 'redis:7-alpine',
    'container_name': 'cyberos-redis-prod',
    'command': ['redis-server', '--maxmemory', '256mb', '--maxmemory-policy', 'allkeys-lru'],
    'ports': ['6379:6379'],
    'restart': 'always',
    'networks': ['default'],
    'logging': data['services']['mongodb']['logging']
}

data['services']['backend']['depends_on']['redis'] = {'condition': 'service_started'}
data['services']['ml_worker']['depends_on']['redis'] = {'condition': 'service_started'}

# Add to requirements
with open('requirements.txt', 'a') as f:
    f.write('\nredis==5.0.1\n')

with open('docker-compose.prod.yml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
