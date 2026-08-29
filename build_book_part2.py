import os

BASE_DIR = r"E:\cyberos-prototype\cyberos-docs"

def write_file(path, content):
    with open(os.path.join(BASE_DIR, path), "w", encoding="utf-8") as f:
        f.write(content.strip())

def build_part2():
    # 02 Theory (cont)
    write_file("docs/02_theory/feature_engineering.md", """
# Feature Engineering and Mathematics

Feature engineering transforms raw logs into numerical values that XGBoost and deterministic rules can understand.

## Inter-Arrival Time (IAT)
The time between consecutive packets in a flow.
$$
IAT_i = t_i - t_{i-1}
$$

* **Why it matters**: Botnet C2 beaconing has very low variance in IAT (highly periodic).

## Shannon Entropy
Measures the randomness of a string.
$$
H(X) = -\\sum p(x) \\log_2 p(x)
$$

* **Why it matters**: DGA (Domain Generation Algorithms) domains like `q9x3vj8.com` have high entropy compared to `google.com`.

## Exfiltration Asymmetry
$$
Ratio = \\frac{Outbound\\ Bytes}{Inbound\\ Bytes}
$$

* **Why it matters**: Standard web traffic pulls more data down than it sends up. If a host sends 1400x more data up than it receives down, it is likely exfiltrating data.

```text
Inbound   █
Outbound  ███████████████████████████
Detector: exfil_v1
```
    """)

    # 03 Threats
    write_file("docs/03_threats/ddos.md", """
# Volumetric DDoS

## What is DDoS?
A Distributed Denial of Service attack attempts to overwhelm a target with traffic.
* **SYN Flood**: Sending TCP SYN packets without completing the handshake.
* **UDP Flood**: Overwhelming a host with connectionless UDP packets.
* **Spoofed Source**: Forging the source IP address.

## Detection Implementation
* **Detector**: `ddos_stat_v1`
* **Features**: `pps` (packets per second), `syn_ratio`
* **Spoofed IP Logic**: We measure Source IP Entropy. If entropy exceeds `2.5` while a host is under load, it indicates randomized spoofing.

## Validation
* **T3**: SYN Flood (Passed)
* **T4**: UDP Flood (Passed)
* **T15**: Spoofed IP (Passed)
    """)

    write_file("docs/03_threats/c2_beaconing.md", """
# Command & Control (C2) Beaconing

## What is C2 Beaconing?
Malware periodically "calls home" to an attacker-controlled server to request instructions. 

## Detection Implementation
* **Detector**: `beacon_stateful_v2`
* **Features**: IAT Mean, IAT Standard Deviation, IAT Coefficient of Variation (CV).
* **Logic**: If a connection to the same destination occurs over multiple windows with an IAT CV near zero, it is a rigid beacon. If it has high statistical periodicity, it is a jittered beacon.

## Validation
* **T5**: Rigid Beacon (Passed)
* **T6**: Jittered Beacon (Passed)
    """)

    write_file("docs/03_threats/dga_tunneling.md", """
# DGA & DNS Tunnelling

## Domain Generation Algorithms (DGA)
Malware generates thousands of random domains to connect to C2 servers, evading static blocklists.
* **Detector**: `dga_lexical_v1`
* **Logic**: Calculates Shannon entropy, numeric ratios, and consonant clustering on the DNS query string.
* **Validation**: T7 (Passed)

## DNS Tunnelling
Using the DNS protocol as a transport layer for non-DNS data (e.g., exfiltrating data via `base64_encoded_data.badguy.com`).
* **Detector**: `dns_tunnel_stateful_v1`
* **Logic**: High volume of queries to the same root domain with large TXT/NULL record types.
* **Validation**: T8 (Passed)
    """)

    write_file("docs/03_threats/encrypted_sessions.md", """
# Encrypted Sessions

## The Constraint: NO DECRYPTION
CyberOS demands we operate entirely on metadata. We cannot decrypt TLS or QUIC payloads.

## Detection Implementation
* **Detector**: `tls_behavioral_v1`
* **Logic**: We analyze the unencrypted TLS handshake (SNI, JA3/JA4 fingerprints) combined with behavioral flow metrics (bytes, timing, directionality). A malware SSL tunnel has a fundamentally different byte distribution than a legitimate HTTPS web browsing session.
* **Validation**: T9 (Passed)
    """)

    write_file("docs/03_threats/recon_exfil_slow.md", """
# Reconnaissance, Exfiltration & Slow HTTP

## Port Scanning
* **Detector**: `scan_v2`
* **Logic**: High fan-out to unique destination ports/IPs. 
* **The T11 FN**: The system missed the T11 Slow Scan because our architecture uses 10-second tumbling windows. A slow scan deliberately evades short temporal thresholds.

## Data Exfiltration
* **Detector**: `exfil_v1`
* **Logic**: Identifies massive directional byte asymmetry (Outbound >> Inbound) to untrusted destinations.
* **Validation**: T12 (Passed)

## Slow HTTP (Slowloris)
* **Detector**: `slow_http_v1`
* **Logic**: Analyzes trickle traffic—concurrent connections holding open sockets by sending 1 byte every few seconds with an incomplete HTTP request.
* **Validation**: T13 (Passed)
    """)

if __name__ == "__main__":
    build_part2()
    print("Part 2 Generated!")
