# ARCHITECTURAL TRUTH (SIH 26145)

## 1. What This System Actually Is
*   A **passive, stateful network detection engine** that evaluates connection flow metadata, DNS query strings, and TLS ClientHello fingerprints.
*   An **evidence correlation platform** that groups isolated chronological alerts by entity (Source IP) into unified `SecurityCases`.
*   A **Next.js Analyst Dashboard** that presents physical alerts via REST and WebSockets without any mock data.

## 2. What This System Is NOT
*   **It is NOT an ML/AI platform.** The Machine Learning components were removed from the ingestion path because deterministic heuristics + state tracking proved superior for baseline adversarial validation without the overhead of feature scaling.
*   **It is NOT an inline IPS.** It cannot block traffic. It operates passively on copies of traffic (PCAP/Diode).
*   **It is NOT a payload inspector.** It performs zero deep-packet decryption.
*   **It is NOT a production Gigabit system.** The core Python detection logic operates at sub-millisecond latencies, but the Scapy-based PCAP parsing caps offline ingestion at roughly ~170 flows/second.

## 3. Verified Capabilities (6 Threat Classes)
*   **DDoS / Scans:** Evaluates tumbling temporal windows for byte variance, packet variance, and rigid TCP flag ratios.
*   **C2 / Tunnels:** Maintains Bounded Deques (Memory-Safe Temporal State) to catch slow/jittered beaconing and track subdomains per base domain.
*   **Encrypted Threats:** Computes JA3 and SNI passively, correlating suspicious TLS handshakes with periodic timing behavior.
*   **Evidence Fusion:** Prevents alert fatigue by rolling distinct detector firings into a single Case timeline, escalating severity intelligently (e.g., DGA + TLS = CRITICAL).

## 4. Known Limitations
*   **Throughput Constraint:** Python's GIL + Scapy string manipulation limits the front-end packet parser. Production deployment would require Zeek or DPDK feeding JSON to this Python detection tier.
*   **State Expiry:** While bounded by maximum counts (e.g., `maxlen=20`), long-lived dormant connections might slip out of the temporal window if the TTL (3600s) clears them before the next packet arrives.
