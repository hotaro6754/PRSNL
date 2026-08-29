with open('docker-compose.prod.yml', 'r') as f:
    content = f.read()
content = content.replace('ML_STAGE=EVALUATION', 'ML_STAGE=PRODUCTION')
with open('docker-compose.prod.yml', 'w') as f:
    f.write(content)
