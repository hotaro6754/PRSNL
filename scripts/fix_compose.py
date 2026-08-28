import yaml

with open('docker-compose.yml', 'r') as f:
    compose = yaml.safe_load(f)

# Add init-redpanda
compose['services']['init-redpanda'] = {
    'image': 'docker.redpanda.com/redpandadata/redpanda:v24.1.1',
    'container_name': 'sih26145-init-redpanda',
    'depends_on': {'redpanda': {'condition': 'service_healthy'}},
    'command': [
        'sh', '-c', 
        'rpk topic create ml-feature-vectors network-observations --brokers=redpanda:9092 || true'
    ],
    'restart': 'on-failure'
}

with open('docker-compose.yml', 'w') as f:
    yaml.dump(compose, f, sort_keys=False)

print("Added init-redpanda service to docker-compose.yml")
