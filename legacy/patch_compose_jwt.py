import yaml

with open('docker-compose.yml', 'r') as f:
    data = yaml.safe_load(f)

for service in ['backend', 'ml_worker', 'zeek_adapter']:
    if 'command' in data['services'][service]:
        cmd = data['services'][service]['command']
        if isinstance(cmd, list) and len(cmd) >= 3 and cmd[1] == '-c':
            if 'PyJWT' not in cmd[2]:
                cmd[2] = cmd[2].replace('pip install ', 'pip install PyJWT ')
                
with open('docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
