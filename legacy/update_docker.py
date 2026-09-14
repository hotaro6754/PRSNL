import yaml

with open('docker-compose.prod.yml', 'r') as f:
    data = yaml.safe_load(f)

# Update init container command
data['services']['redpanda_init']['command'] = [
    'sh', '-c', 
    'rpk topic create network-observations -p 8 --brokers redpanda:9092 || true && '
    'rpk topic create network-observations-dlq -p 8 --brokers redpanda:9092 || true && '
    'rpk topic create feature-vectors -p 8 --brokers redpanda:9092 || true && '
    'rpk topic create ml-predictions -p 8 --brokers redpanda:9092 || true'
]

# Ensure we scale the backend as well to test stateful window manager across partitions
data['services']['backend']['deploy'] = {'replicas': 4}
if 'container_name' in data['services']['backend']:
    del data['services']['backend']['container_name']
# Because backend binds to port 8000, setting replicas to 4 will cause port conflicts unless we remove the port binding.
if 'ports' in data['services']['backend']:
    del data['services']['backend']['ports']

with open('docker-compose.prod.yml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
