import os

BASE_DIR = r"E:\sih26145-prototype\ps26145-docs"
DOCS_DIR = os.path.join(BASE_DIR, "docs")

def create_dirs():
    dirs = [
        "01_basics", "02_theory", "03_threats", "04_intelligence",
        "05_architecture", "06_operations", "07_governance", "08_dossier", "assets/screenshots"
    ]
    for d in dirs:
        os.makedirs(os.path.join(DOCS_DIR, d), exist_ok=True)

def write_file(path, content):
    with open(os.path.join(BASE_DIR, path), "w", encoding="utf-8") as f:
        f.write(content.strip())

mkdocs_yml = """
site_name: PS26145 Technical Book
site_description: Deep technical publication for PS26145
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - toc.integrate
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.tabs.link
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.tabbed:
      alternate_style: true
  - toc:
      permalink: true

extra_javascript:
  - javascripts/mathjax.js
  - https://polyfill.io/v3/polyfill.min.js?features=es6
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js

nav:
  - Home: index.md
  - 1. Basics:
    - 01_basics/networks.md
    - 01_basics/soc_and_ndr.md
    - 01_basics/ps26145_problem.md
  - 2. Theory:
    - 02_theory/zeek.md
    - 02_theory/canonical_observation.md
    - 02_theory/feature_engineering.md
  - 3. Threats:
    - 03_threats/ddos.md
    - 03_threats/c2_beaconing.md
    - 03_threats/dga_tunneling.md
    - 03_threats/encrypted_sessions.md
    - 03_threats/recon_exfil_slow.md
  - 4. Intelligence:
    - 04_intelligence/deterministic.md
    - 04_intelligence/ml_from_zero.md
    - 04_intelligence/xgboost.md
    - 04_intelligence/v4_to_v5_case_study.md
    - 04_intelligence/evidence_fusion.md
  - 5. Architecture:
    - 05_architecture/streaming.md
    - 05_architecture/redis_entity.md
    - 05_architecture/window_manager.md
    - 05_architecture/soc_dashboard.md
  - 6. Operations:
    - 06_operations/installation.md
    - 06_operations/running.md
    - 06_operations/training.md
    - 06_operations/testing_benchmarking.md
    - 06_operations/troubleshooting.md
    - 06_operations/hardware_deployment.md
  - 7. Governance & Research:
    - 07_governance/model_governance.md
    - 07_governance/research_library.md
  - 8. Dossier:
    - 08_dossier/jury_mode.md
    - 08_dossier/history_and_verdict.md
"""

index_md = """
# Welcome to the PS26145 Knowledge System

**A Quarkdown-inspired cybersecurity research textbook, implementation manual, architecture reference, engineering diary, and validation dossier.**

## Start From Zero
If you have zero cybersecurity knowledge, begin at [Basics: Computer Networks](01_basics/networks.md) and progress chapter by chapter.

## Interactive Learning
Throughout this book, you will find:
* **Interactive Mermaid Diagrams**: Architecture flows, data pipelines, and threat vectors.
* **Mathematical Notation**: Formal definitions for entropy, IAT, and byte asymmetry.
* **Engineering Reality**: We do not hide failures. See the [V4 to V5 Case Study](04_intelligence/v4_to_v5_case_study.md) for how a feature parity mismatch broke the system, and how it was fixed.
"""

mathjax_js = """
window.MathJax = {
  tex: {
    inlineMath: [["\\\\(", "\\\\)"]],
    displayMath: [["\\\\[", "\\\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};
"""

def build_part1():
    create_dirs()
    write_file("mkdocs.yml", mkdocs_yml)
    write_file("docs/index.md", index_md)
    os.makedirs(os.path.join(DOCS_DIR, "javascripts"), exist_ok=True)
    write_file("docs/javascripts/mathjax.js", mathjax_js)
    
    # 01 Basics
    write_file("docs/01_basics/networks.md", """
# Computer Networks from Zero

> "I know almost nothing about cybersecurity."

Welcome. To understand Network Detection and Response (NDR), we must first understand the network.

## What is a network?
A network is two or more computers connected together to share data. 

## Key Concepts

* **IP Address**: The logical address of a computer. Example: `192.168.1.5`.
* **Port**: A logical channel on a computer. Example: Port `443` is for secure web traffic (HTTPS).
* **Packet**: The single unit of network communication. When you send a file, it is broken down into packets.
* **TCP (Transmission Control Protocol)**: A reliable way to send packets. It ensures packets arrive in order.
* **UDP (User Datagram Protocol)**: A fast, best-effort way to send packets. Used for video streams or DNS.
* **DNS (Domain Name System)**: The phonebook of the internet (translates `google.com` to `142.250.190.46`).

## Packets vs. Flows

A **Packet** is a single unit. A **Flow** is multiple packets belonging to the same communication (same source IP, destination IP, source port, destination port, and protocol).

```mermaid
flowchart LR
    A[Packet 1] --> F[Flow]
    B[Packet 2] --> F
    C[Packet 3] --> F
    D[Packet N] --> F
```

NDR systems process *flows* because threats are behavioral over time. A single packet doesn't show a pattern; a flow does.
    """)
    
    write_file("docs/01_basics/soc_and_ndr.md", """
# SOC and NDR

## What is a SOC?
A **Security Operations Center (SOC)** is the facility where an organization's security team monitors and analyzes the security posture. 

```mermaid
flowchart LR
    A[Network Event] --> B[Detection]
    B --> C[Alert]
    C --> D[Correlation]
    D --> E[Security Case]
    E --> F[SOC Analyst]
```

## What is NDR?
**Network Detection and Response (NDR)** analyzes raw network traffic to detect threats. 

| Technology | Sees Network | Active Response | Primary Purpose |
| ---------- | ------------ | --------------- | --------------- |
| **NIDS** | Yes | No | Detect threats (signature based) |
| **IPS** | Yes | Yes | Block threats inline |
| **SIEM** | No (Uses Logs) | No | Log aggregation & alerting |
| **NDR** | Yes | Yes (via integration) | Behavioral ML threat detection |

PS26145 is a purely passive NDR solution.
    """)
    
    write_file("docs/01_basics/ps26145_problem.md", """
# PS26145 — The Actual Problem

## Why Unidirectional Network Monitoring?
High-security environments (like Government enclaves) cannot risk an attacker using the security tool itself to send data *back* into the production network.

We use **SPAN/TAPs** or **Hardware Data Diodes** to enforce this physically.

```mermaid
flowchart LR
    N[Production Network]
    P[Passive Mirror / TAP / Data Diode]
    E[Monitoring Enclave]

    N --> P --> E
    E -. NO RETURN PATH .-> N
```
*Note: Software passivity (read-only code) and physical one-way enforcement (data diode) are separate concepts. This project implements software passivity, pending physical diode hardware validation.*

## The PS26145 Requirement Matrix

| PS Requirement | Implementation | Evidence | Status |
| :--- | :--- | :--- | :--- |
| Passive Ingestion | `zeek_adapter.py` | Container PCAP replay | VERIFIED |
| No Payload Decryption | Metadata only | `NetworkObservation` schema | VERIFIED |
| Volumetric DDoS | `ddos_stat_v1` | T3, T4, T15 | VERIFIED |
| C2 Beaconing | `beacon_stateful_v2`| T5, T6 | VERIFIED |
| DGA / Tunnelling | `dga_lexical_v1` | T7, T8 | VERIFIED |
| Encrypted Sessions | `tls_behavioral_v1`| T9 | VERIFIED |
| Reconnaissance | `scan_v2` | T10 | VERIFIED |
| Data Exfiltration | `exfil_v1` | T12 | VERIFIED |

## Why Passive Detection is Hard
Passive systems cannot:
* Probe a host to see if it is alive.
* Grab banners from ports.
* Send TCP RST to kill a bad connection.

We must infer behavior purely from metadata: timing, entropy, state, and bytes.
    """)

    # 02 Theory
    write_file("docs/02_theory/zeek.md", """
# Zeek Network Security Monitor

## What is Zeek?
Zeek is a passive, open-source network traffic analyzer. Unlike Wireshark, which shows you raw packets, Zeek provides highly structured metadata logs.

```mermaid
flowchart LR
    A[Network Traffic] --> B[Zeek]
    B --> C[conn.log]
    B --> D[dns.log]
    B --> E[ssl.log / TLS Metadata]
```

## Zeek Semantics
* **Originator**: The IP that started the connection (the client).
* **Responder**: The IP that received the connection (the server).
* **TCP History**: A string (e.g., `ShADadFf`) describing the sequence of TCP flags seen.

Zeek clusters can scale to 100Gbps on physical interfaces using AF_PACKET or PF_RING.
    """)

    write_file("docs/02_theory/canonical_observation.md", """
# Canonical Observation

Our machine learning pipeline originally failed because it was trained on PCAP features extracted by Python's `Scapy`, but deployed on production streams from `Zeek`. 

## The Parity Failure
* `byte_count` on Scapy included L2 Ethernet headers (e.g., 13,600).
* `byte_count` on Zeek only counted L3 IP payloads (e.g., 1,500).

```mermaid
flowchart LR
    A[Zeek]
    B[Scapy / Training Sources]
    A --> C[CanonicalObservation]
    B --> C
    C --> D[Feature Engine]
```
The **CanonicalObservation** is an intermediate schema that forces both training data and production data into the exact same semantic representation.
    """)

if __name__ == "__main__":
    build_part1()
    print("Part 1 Generated!")
