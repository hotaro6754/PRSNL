# CyberOS PHYSICAL HARDWARE-LAB VALIDATION GUIDE

This bundle is for use ONLY on an authorized Linux hardware host equipped with a physical monitoring NIC, and optionally an enterprise SPAN/TAP/Hardware Data Diode.

DO NOT execute these steps on a Windows, WSL2, or synthetic Docker bridge environment.

## Operator Sequence

1. **install prerequisites:** Run `./sensor_setup.sh` to prepare the Linux host (Zeek, Docker, dependencies).
2. **identify monitoring NIC:** Determine the physical interface designated for passive monitoring.
3. **configure SPAN/TAP/data diode:** Physically cable the environment. If using a data diode, verify one-way optical/physical enforcement.
4. **start sensor:** Launch `docker-compose -f docker-compose.hardware.yml up -d` using the identified physical interface (with `network_mode: host` or correct macvlan configuration).
5. **verify tcpdump:** Validate raw packet arrival on the physical NIC.
6. **verify Zeek:** Validate Zeek is generating `conn.log`, `dns.log`, `ssl.log` from live traffic.
7. **verify Redpanda:** Validate the Zeek Adapter is publishing to the Kafka broker.
8. **verify ML:** Validate XGBoost V5 workers are consuming and scoring streaming `FeatureVector`s.
9. **verify dashboard:** Validate the Next.js UI is consuming live `SecurityCase`s via WebSockets.
10. **run threat matrix:** Replay or generate live threat traffic (DDoS, Exfil, Slowloris, etc.) across the physical boundary.
11. **run soak:** Perform a continuous 1-hour (preferred 6-hour) live traffic soak without restarts.
12. **capture metrics:** Execute `./validation_harness.sh` to extract packet drops, memory stability, Kafka lag, and system performance.
13. **determine final status:** Map findings to the physical acceptance gates.

## Diagnostic Commands

Run these on the Linux sensor to validate Gate A & B (Packet Arrival):

```bash
# Interface discovery
ip -br link
ip addr

# Check RX counters and drops
ip -s link show <MONITOR_INTERFACE>

# Check hardware offloads (LRO, GRO, etc.)
ethtool -k <MONITOR_INTERFACE>
ethtool -S <MONITOR_INTERFACE>

# Verify raw packet arrival (must not be zero)
tcpdump -ni <MONITOR_INTERFACE> -c 500
```

Run these to validate downstream health:

```bash
# Kafka lag
docker exec redpanda-1 rpk group describe inference_group

# MongoDB Case inspection
docker exec mongodb mongosh cyberos_prod --eval 'db.cases.countDocuments({})'
```
