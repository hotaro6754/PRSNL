import re

with open('backend/inject_live_regression.py', 'r') as f:
    code = f.read()

code = code.replace(
    'from kafka import KafkaProducer',
    'from confluent_kafka import Producer'
)

# Update producer init
code = code.replace(
    'producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER, value_serializer=lambda v: json.dumps(v).encode("utf-8"))',
    '''producer = Producer({'bootstrap.servers': KAFKA_BROKER})
def delivery_report(err, msg):
    pass
'''
)

# Update producer send
code = re.sub(
    r'producer\.send\(KAFKA_TOPIC,\s*obs\)',
    'producer.produce(KAFKA_TOPIC, json.dumps(obs).encode("utf-8"), callback=delivery_report)',
    code
)

code = code.replace('producer.flush()', 'producer.flush()')

with open('backend/inject_live_regression.py', 'w') as f:
    f.write(code)
print('Updated inject_live_regression.py to use confluent_kafka')
