import re

with open('backend/inject_live_regression.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_main = False
for line in lines:
    if line.startswith('if __name__ == "__main__":'):
        in_main = True
        new_lines.append(line)
        new_lines.append('''    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    def delivery_report(err, msg):
        pass

    print("Injecting T1-T15 Regression flows into Live Pipeline...")
    flows = generate_flows()
    import random
    random.shuffle(flows)
    import json
    for f in flows:
        producer.produce('network-observations', json.dumps(f).encode("utf-8"), callback=delivery_report)
    producer.flush()
    print(f"Injected {len(flows)} flows successfully. Check the dashboard!")
''')
        break
    else:
        new_lines.append(line)

with open('backend/inject_live_regression.py', 'w') as f:
    f.writelines(new_lines)
print('Rewrote main block')
