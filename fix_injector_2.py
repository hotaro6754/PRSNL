import re

with open('backend/inject_live_regression.py', 'r') as f:
    code = f.read()

# Strip out any remaining KafkaProducer
code = re.sub(
    r'producer = KafkaProducer\([\s\S]*?\)',
    '''producer = Producer({'bootstrap.servers': KAFKA_BROKER})
def delivery_report(err, msg):
    pass''',
    code
)

with open('backend/inject_live_regression.py', 'w') as f:
    f.write(code)
print('Fixed multiline KafkaProducer')
