# NTRO Sentinel-26145: Architecture, Implementation & Setup Guide
## AI-Based Detection of Cyber Threats in Unidirectional IP Traffic Across Physical Data Diodes

---

## 1. Executive Summary & Problem Statement (PS #26145)

### Background & Context
Critical infrastructure operators (power grids, nuclear plants, defense operations, intelligence networks) observe their high-security enclaves and peering links using **hardware data diodes** (e.g., Fox-IT, Advenica, Owl Cyber Defense) or **passive optical fiber splitters**. These physical devices allow light to travel in **one direction only** into a monitoring enclave.

### The Unidirectional Security Paradox
* **The Benefit**: The monitoring system is physically air-gapped from transmitting back into the production network. Even if the monitoring enclave is compromised, it cannot serve as a pivot into the core network. Furthermore, passive taps preserve an immutable, unadulterated chain of custody for forensic use.
* **The Challenge**: The detection engine must operate **purely from passive ingress observation**. 
  * It **cannot** complete a TCP 3-way handshake.
  * It **cannot** send TCP Resets (`RST`) or ICMP Unreachable messages.
  * It **cannot** perform active vulnerability scans, banner grabs, or TLS interception.
  * Bidirectional flow counters (`resp_packets`, `resp_bytes`) are permanently zero ($0$).

**NTRO Sentinel-26145** is purpose-built to solve this challenge through a multi-tier passive detection fabric combining statistical physics, streaming window aggregation, and dual-layer AI/ML inference.

---

## 2. Threat Vectors & Passive Detection Mathematics

Traditional intrusion detection systems rely heavily on TCP response flags (e.g., `SYN-ACK`, `RST`) to infer connection states. In a unidirectional enclave, alternative mathematical formulations must be used:

### Vector (a): Volumetric SYN Flood (DDoS)
* **Threat Mechanism**: Flooding edge firewalls or internal services with rapid TCP `SYN` packets without completing handshakes.
* **Simplex Mathematical Formulation**:
  $$	ext{Asymmetry Ratio } R_{syn} = rac{N_{syn}}{N_{ack} + 1} 	o \infty$$
  $$	ext{Volumetric Gradient } rac{\Delta P}{\Delta t} > 	au_{vol}$$
* **Passive Attribution**: Extreme arrival surges of unacknowledged SYN frames without return handshakes.

### Vector (b): Botnet C2 Periodic Beaconing
* **Threat Mechanism**: Compromised internal hosts pinging external Command & Control infrastructure using fixed or jittered heartbeats.
* **Simplex Mathematical Formulation**:
  $$	ext{Inter-Arrival Time (IAT) Coefficient of Variation: } CV = rac{\sigma_{iat}}{\mu_{iat}}$$
  * When $CV < 0.5$, packet intervals exhibit rigid robotic periodicity characteristic of automated C2 beaconing.
  * When $CV \ge 1.0$, packet intervals indicate Poisson-distributed human interactive traffic.

### Vector (c): DNS Covert Tunnelling & DGA
* **Threat Mechanism**: Exfiltrating sensitive data chunks or resolving algorithmic rendezvous points encoded in subdomain labels (e.g., `7a89b1c2.tunnel.defense.gov`).
* **Simplex Mathematical Formulation**:
  $$	ext{Shannon Entropy: } H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$
  * English domain names average $H pprox 2.4 - 3.2$ bits/character.
  * Base64/Hex-encoded covert tunnels and DGAs exhibit $H > 3.8$ bits/character.

### Vector (d): Encrypted Session Metadata Anomalies
* **Threat Mechanism**: Malicious binaries establishing TLS sessions with non-standard cipher suites, abnormal extensions, or suspicious record length sequences.
* **Simplex Formulation**: Passive JA3 / JA4 hash extraction from unencrypted TLS `ClientHello` packets:
  $$	ext{JA3} = 	ext{MD5}(	ext{SSLVersion},	ext{Ciphers},	ext{Extensions},	ext{EllipticCurves},	ext{PointFormats})$$

### Vector (e): Simplex Reconnaissance & Horizontal Scans
* **Threat Mechanism**: Adversaries mapping active edge services by firing single probes across IP and port ranges.
* **Simplex Formulation**:
  $$	ext{Port Fan-out: } rac{|	ext{Distinct Destination Ports}|}{\Delta t} > 	heta_{ports}$$
  $$	ext{Host Fan-out: } rac{|	ext{Distinct Destination IPs}|}{\Delta t} > 	heta_{hosts}$$

### Vector (f): Asymmetric Data Exfiltration
* **Threat Mechanism**: Bulk staging and transfer of confidential data outward through the unidirectional tap.
* **Simplex Formulation**:
  $$	ext{Volume Ratio: } rac{	ext{Bytes}_{out}}{	ext{Bytes}_{in} + 1} > 10	imes$$

---

## 3. End-to-End System Architecture

```
[Production Network / Tap Link]
              │
              ▼ (100% Simplex Optical Splitter - 0 Return ACKs)
  ┌────────────────────────────────────────────────────────┐
  │         NTRO Sentinel-26145 Monitoring Enclave         │
  │                                                        │
  │  ┌───────────────────────┐  ┌───────────────────────┐  │
  │  │ Live Scapy Sniffer    │  │ Zeek Simplex Tap      │  │
  │  │ (Interface: eth0)     │  │ (conn.log, dns.log)   │  │
  │  └───────────┬───────────┘  └───────────┬───────────┘  │
  │              │                          │              │
  │              ▼                          ▼              │
  │   ┌─────────────────────────────────────────────────┐  │
  │   │ Redpanda (Kafka v24.1) Ingestion Pipeline       │  │
  │   │ Topic: network-observations                     │  │
  │   └────────────────────────┬────────────────────────┘  │
  │                            ▼                           │
  │   ┌─────────────────────────────────────────────────┐  │
  │   │ Tumbling & Sliding Window Manager (5s windows)  │  │
  │   └────────────────────────┬────────────────────────┘  │
  │                            ▼                           │
  │   ┌─────────────────────────────────────────────────┐  │
  │   │ Dual AI/ML Inference Pipeline                   │  │
  │   │  • Model 1: XGBoost v5.0.0 (Supervised)         │  │
  │   │  • Model 2: Isolation Forest v2.0.0 (Anomaly)   │  │
  │   │  • Heuristics: Shannon Entropy + IAT CV         │  │
  │   └────────────────────────┬────────────────────────┘  │
  │                            ▼                           │
  │   ┌─────────────────────────────────────────────────┐  │
  │   │ Forensic Evidence Ledger (MongoDB 7 + Redis 7)  │  │
  │   └────────────────────────┬────────────────────────┘  │
  │                            ▼                           │
  │   ┌─────────────────────────────────────────────────┐  │
  │   │ Next.js 16 Web Console & Prometheus Metrics      │  │
  │   └─────────────────────────────────────────────────┘  │
  └────────────────────────────────────────────────────────┘
```

### Key Components:
1. **Passive Ingestion Engine (`backend/ingestion/live_sniffer.py`)**:
   * Uses Scapy with low-level socket binding (`cap_add: [NET_ADMIN, NET_RAW]`) on `eth0`.
   * Automatically extracts directional IP header metrics, TCP flags (`SYN`, `FIN`, `RST`), and UDP DNS payloads.
   * Auto-starts on backend initialization.
2. **Streaming Event Bus (`cyberos-redpanda`)**:
   * High-throughput Redpanda cluster receiving flow records at line rate without socket bottlenecks.
3. **Window Manager (`backend/streaming/window_manager.py`)**:
   * Aggregates micro-flows into temporal feature windows per source entity.
4. **Dual AI/ML Inference Engine (`backend/ml/`)**:
   * **XGBoost Classifier (v5.0.0)**: Evaluates 12 engineered simplex flow features (packet velocity, byte asymmetry, IAT variance, entropy).
   * **Isolation Forest (v2.0.0)**: Trained on UNSW-NB15 to catch novel zero-day behavioral deviations.
5. **Next.js 16 Frontend UI (`frontend/`)**:
   * **Live Threat Console (`/`)**: Real-time ingress flow stream with automatic severity ranking.
   * **Case Investigation (`/cases/[id]`)**: Detailed threat attribution, mathematical metrics, and interactive Wireshark protocol tree dissection.
   * **Attack Replay Lab (`/simulator`)**: Launch Scapy/PCAP replay simulations mapped directly to Kali Linux tool commands.
   * **Flow Analytics (`/analytics`)**: Time-series volume and entropy charts.
   * **Enclave Health (`/health`)**: Diagnostic telemetry across all sensors and models.

---

## 4. Kali Linux Tool Mapping & Verification Lab

To thoroughly test the unidirectional detection engine, administrators and analysts can map standard Kali Linux red team utilities directly to Sentinel's passive classifiers:

| Threat Vector | Kali Linux Tool Command | Sentinel-26145 Passive Detection Mechanism |
| :--- | :--- | :--- |
| **Volumetric SYN Flood** | `hping3 -S -p 80 --flood <target_ip>` | Detection of extreme arrival bursts with 100% unacknowledged SYN flags. |
| **Stealth Recon Scan** | `nmap -sS -Pn -p 1-1000 <target_ip>` | Detection of rapid sequential destination port fan-out across simplex tap. |
| **Covert DNS Tunneling** | `dnscat2 --dns domain=exfil.covert.lab` | Shannon Entropy ($H > 3.8$) in subdomain queries and TXT record lengths. |
| **C2 Periodic Beaconing** | `sliver-client beacon --interval 10s` | IAT Coefficient of Variation ($CV < 0.5$) proving automated heartbeats. |
| **Service Brute Force** | `hydra -l admin -P wordlist.txt <target> ssh` | High-frequency connection attempts on isolated service ports. |
| **Forensic Inspection** | `tshark -r <capture.pcap> -q -z conv,ip` | Protocol breakdown, Wireshark tree parsing, and raw hex/ASCII inspection. |

---

## 5. Quickstart & Setup Guide

### Prerequisites
* **Docker Desktop** (version 24.0 or higher)
* **Docker Compose** (version 2.20 or higher)
* **Python 3.10+** (for running external aggressive verification scripts)
* At least **4 GB RAM** and **10 GB Disk Space**

### Step 1: Clone the Repository
```bash
git clone -b feature/ntro-pure-unidirectional https://github.com/hotaro6754/CYBER-OS.git
cd CYBER-OS
```

### Step 2: Launch the Microservice Stack
```bash
docker compose up -d --build
```

### Step 3: Verify Container Health
Wait ~20 seconds for all containers to initialize:
```bash
docker compose ps
```
All containers should report `Up` or `Healthy`:
* `cyberos-frontend` (Port 3000)
* `cyberos-backend` (Port 8000)
* `cyberos-redpanda` (Port 9644, 19092)
* `cyberos-mongodb` (Port 27017)
* `cyberos-redis` (Port 6379)
* `cyberos-zeek`
* `cyberos-prometheus` (Port 9090)
* `cyberos-grafana` (Port 3001)

### Step 4: Run the Aggressive Verification Suite
Execute the automated test runner to validate all 6 threat vectors and mathematical detection engines:
```bash
python tests_ntro_aggressive.py
```
**Expected Output**:
```text
================================================================================
          NTRO SENTINEL-26145 AGGRESSIVE TEST SUITE REPORT
================================================================================
Total Test Cases: 13 | Passed: 13 | Failed: 0 | Elapsed: 5.73s
>>> VERIFICATION RESULT: 100% PASS - PRODUCTION READY FOR NTRO PS #26145 <<<
================================================================================
```

---

## 6. System Port & API Reference

| Service | Port | Description |
| :--- | :--- | :--- |
| **Web Console** | `3000` | Next.js 16 SOC Dashboard (`http://localhost:3000`) |
| **FastAPI Backend** | `8000` | REST & WebSocket API (`http://localhost:8000/docs`) |
| **Health Check** | `8000` | Detailed enclave status (`http://localhost:8000/health`) |
| **Prometheus** | `9090` | Time-series metric scraper (`http://localhost:9090`) |
| **Grafana** | `3001` | Infrastructure dashboards (`http://localhost:3001`, `admin`/`admin`) |
| **Redpanda Console** | `9644` | Streaming topic administrator |
| **MongoDB** | `27017` | Immutable case and evidence database |

### Key API Endpoints:
* `GET /api/cases`: Fetch active and contained threat cases.
* `GET /api/cases/{case_id}`: Fetch case details with 5-layer decision explanation (supports 8-char short IDs and 36-char UUIDs).
* `GET /api/cases/{case_id}/packet_demo`: Fetch Wireshark protocol tree dissection and hex dump.
* `POST /api/cases/{case_id}/close`: Mark case contained/closed.
* `GET /api/network/sniffer/status`: Query live promiscuous sniffer status.
* `POST /api/network/sniffer/start`: Start live packet capture on interface (`eth0`).
* `POST /api/network/sniffer/stop`: Stop live packet capture.
* `POST /api/scan`: Run single-flow ML classification against XGBoost and Isolation Forest.
* `POST /api/simulate/{attack_type}`: Inject raw socket simplex attack streams.

---

## 7. Security & Compliance Verification

* **Physical Simplex Assurance**: Zero reverse packets are transmitted across the monitoring link.
* **No Decryption Required**: AI models inspect only unencrypted IP metadata, timing distributions, and Shannon entropy.
* **Forensic Chain of Custody**: Cryptographic hashes are attached to all captured observations.
