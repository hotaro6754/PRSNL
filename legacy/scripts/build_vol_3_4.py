import os

OUTPUT_DIR = r"E:\cyberos-prototype\cyberos-docs\docs\handbook"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_file(filename, content):
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# ==========================================
# VOLUME 3: NETWORK DEFENSE & NDR
# ==========================================
VOL3_CONTENT = """
# Volume 3: Network Defense & NDR

## Chapter 21: Firewalls (The Perimeter)
A firewall sits at the edge of the network, acting as a bouncer. It uses stateful inspection to permit or deny traffic based on IP, Port, and Protocol. However, firewalls only look at the envelope, not the letter. If an attacker tunnels data over port 443, the firewall blindly permits it.

## Chapter 22: IDS and IPS
* **Intrusion Detection System (IDS)**: Analyzes traffic for known threat signatures (like an antivirus). It is passive and alerts the SOC.
* **Intrusion Prevention System (IPS)**: Sits inline and blocks traffic immediately if it matches a signature.
The flaw in legacy IDS/IPS is their reliance on signatures. If the malware is a zero-day (never seen before), the signature engine fails.

## Chapter 23: SIEM
Security Information and Event Management (SIEM) aggregates logs from endpoints, firewalls, and active directories. SIEMs lack deep visibility into the raw network wires.

## Chapter 24: Passive vs Active Defense
Active defense actively blocks traffic (IPS, Firewalls). Passive defense merely observes, generating intelligence without risking network disruption. CyberOS is strictly passive.

## Chapter 25: The SOC
The Security Operations Center (SOC) is the human element. An NDR system must not flood the SOC with false positives. Alert fatigue causes analysts to ignore critical warnings.

## Chapter 26: The Architecture of Zeek
Zeek is a passive network traffic analyzer. Unlike Wireshark which decodes raw packets, Zeek produces structured, semantic metadata.
```mermaid
flowchart TD
    A[Raw Packets] --> B[Event Engine]
    B --> C[Policy Scripts]
    C --> D[conn.log]
    C --> E[dns.log]
```

## Chapter 27: Taps and SPAN Ports
To monitor a network passively, you must copy the traffic. 
* **SPAN Port (Port Mirroring)**: The network switch sends a copy of all traffic to a monitoring port.
* **Network TAP**: A physical hardware device spliced into the fiber optic cable that duplicates the light signal. TAPs are completely invisible to the network.

## Chapter 28: PCAP Analysis
Packet Capture (PCAP) files are the ground truth of network analysis. When a SOC analyst investigates a CyberOS alert, they pull the raw PCAP to verify the telemetry.

## Chapter 29: Behavioral Heuristics
Instead of looking for a specific malware signature (`hash=XYZ123`), behavioral heuristics look for the *actions* of malware. (e.g., "This device is contacting 500 IPs per second").

## Chapter 30: Threat Intelligence Fusion
No single detection is absolute. True NDR systems cross-reference internal heuristics with external Threat Intelligence (lists of known bad IPs and domains) to increase confidence.
"""

# ==========================================
# VOLUME 4: THE CyberOS ARCHITECTURE
# ==========================================
VOL4_CONTENT = """
# Volume 4: The CyberOS Architecture

## Chapter 31: The Unidirectional Problem
High-security enclaves (e.g., military, nuclear) cannot risk their security tools becoming attack vectors. Thus, the CyberOS mandate requires a **Unidirectional Network Monitoring System**. The system must receive traffic, process it, and alert the SOC, with zero physical or software capability to send packets *back* into the enclave.

## Chapter 32: Asynchronous Streaming
If traffic spikes to 10Gbps, a monolithic Python script will crash. CyberOS uses an asynchronous streaming architecture to decouple ingestion (Zeek) from processing (XGBoost).

## Chapter 33: Kafka and Redpanda
We utilize **Redpanda**, a Kafka-compatible message broker written in C++. 
```mermaid
sequenceDiagram
    participant Zeek
    participant Redpanda
    participant ML_Worker
    Zeek->>Redpanda: Publish 10,000 flows
    Note over Redpanda: Buffered safely to disk
    ML_Worker->>Redpanda: Consume at own pace
```

## Chapter 34: Redis State Management
Network behavior occurs over time. We use **Redis** (an in-memory key-value store) to maintain the state of every IP address on the network. If an IP isn't seen for 5 minutes, its state gracefully expires via Redis TTL (Time-To-Live).

## Chapter 35: Tumbling Windows
Network traffic never stops. We chunk the infinite stream into 10-second **Tumbling Windows**. Every 10 seconds, the window flushes its statistical aggregates (pps, bytes, entropy) to the ML engine, and resets to zero.

## Chapter 36: The Canonical Observation Layer
This was our greatest engineering hurdle. Our ML model (V4) was trained on Scapy (L2 bytes) but deployed on Zeek (L3 bytes). The semantic mismatch caused catastrophic failure. 
We built the **Canonical Observation Layer**, a strict Pydantic schema that forces all training and production data into the exact same semantic representation.

## Chapter 37: The V4 to V5 Case Study
To fix the V4 hallucination, we re-ran our entire training dataset through an offline Zeek engine, retrained the XGBoost model, and deployed V5. Precision instantly recovered to 99.3%.

## Chapter 38: Microservices and Fault Tolerance
CyberOS is containerized using Docker. 
* If a worker crashes, Redpanda's Consumer Group rebalances the load.
* If MongoDB goes down, workers cache their offsets until it returns.

## Chapter 39: The React WebSockets Dashboard
The SOC frontend is built in React. It connects to the Python backend via WebSockets to stream live alerts at 60 frames per second.
![Dashboard UI](../../assets/screenshots/dashboard_full.png)

## Chapter 40: Zero-Trust Deployment
In production, CyberOS resides on a completely isolated management VLAN. It pulls data from a Data Diode (hardware enforcing one-way flow).
"""

def generate():
    write_file("03_volume_3.md", VOL3_CONTENT)
    write_file("04_volume_4.md", VOL4_CONTENT)
    print("Volumes 3 and 4 (Chapters 21-40) generated successfully.")

if __name__ == "__main__":
    generate()
