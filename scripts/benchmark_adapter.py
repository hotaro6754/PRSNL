import time
import json
import os

print("Writing 100k lines to mock_conn.log...")
base_line = json.dumps({"ts": time.time(), "uid": "CXXX", "id.orig_h": "192.168.1.100", "id.resp_h": "10.0.5.5", "id.orig_p": 12345, "id.resp_p": 443, "proto": "tcp", "duration": 1.0, "orig_bytes": 500, "resp_bytes": 5000, "orig_pkts": 5, "resp_pkts": 10}) + "\n"

with open("mock_conn.log", "w") as f:
    for i in range(100000):
        f.write(base_line)

print("Appending to live zeek log (adapter will pick it up)...")
os.system("docker cp mock_conn.log sih26145-zeek-prod:/tmp/mock_conn.log")
start = time.perf_counter()
os.system("docker exec sih26145-zeek-prod sh -c 'cat /tmp/mock_conn.log >> /var/log/zeek/conn.log'")

# Poll the backend stats endpoint instead of kafka locally
import urllib.request
initial_stats = json.loads(urllib.request.urlopen("http://localhost:8000/api/stats").read())
start_flows = initial_stats["flows_processed"]

while True:
    try:
        stats = json.loads(urllib.request.urlopen("http://localhost:8000/api/stats").read())
        processed = stats["flows_processed"] - start_flows
        if processed >= 100000:
            break
        print(f"Processed: {processed}/100000...")
        time.sleep(1.0)
    except Exception as e:
        pass

end = time.perf_counter()
duration = end - start
print(f"Processed 100k in {duration:.2f}s -> {100000/duration:.2f} fps")
