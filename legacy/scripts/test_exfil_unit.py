from backend.detectors.exfil import ExfiltrationDetector
from backend.contracts.observation import NetworkObservation
import time

det = ExfiltrationDetector()

obs = NetworkObservation(
    observation_id="test_obs",
    flow_id="test",
    source_ip="1.1.1.1",
    destination_ip="2.2.2.2",
    protocol=6,
    source_port=12345,
    destination_port=80,
    orig_packets=100,
    resp_packets=10,
    orig_ip_bytes=1500000,
    resp_ip_bytes=1000,
    first_seen=int(time.time()),
    last_seen=int(time.time()),
    timestamp=int(time.time() * 1000),
    duration=65.0,
    src2dst_bytes=1500000,
    dst2src_bytes=1000
)

alerts = det.evaluate_window([obs], int(time.time() * 1000))
print(f"Alerts generated: {len(alerts)}")
if alerts:
    print(alerts[0].threat_class)
