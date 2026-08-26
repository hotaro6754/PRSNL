import os

BASE_DIR = r"E:\sih26145-prototype\ps26145-docs"

def write_file(path, content):
    with open(os.path.join(BASE_DIR, path), "w", encoding="utf-8") as f:
        f.write(content.strip())

def build_part4():
    # 06 Operations
    write_file("docs/06_operations/installation.md", """
# Installation & Configuration

## Prerequisites
* Python 3.10+
* Docker Desktop (or Linux Docker daemon)
* Git

## Directory Structure
```text
sih26145-prototype/
├── backend/
│   ├── detectors/
│   ├── ml/
│   └── streaming/
├── frontend/
├── tests/
├── models/
└── deployment/
```

## Running the Stack
```bash
docker-compose up -d redis redpanda mongodb
```
*Expected Output*: Containers spin up cleanly.
*Common Failure*: Port 6379 already in use (stop local Redis).
    """)

    write_file("docs/06_operations/running.md", """
# Running the System

```mermaid
flowchart TD
    A[Start Infrastructure] --> B[Start Backend Worker]
    B --> C[Start ML Worker]
    C --> D[Run Web Frontend]
    D --> E[Inject Traffic]
```

## Start Services
1. `python backend/main.py`
2. `python backend/ml_worker.py`
3. `cd frontend && npm start`
    """)

    write_file("docs/06_operations/training.md", """
# Training from Scratch

## Pipeline
Dataset PCAP &rarr; Zeek Adapter &rarr; Canonical JSON &rarr; `train_v5.py` &rarr; `xgboost_v5.bin`

## Reproducibility
The V5 model achieved 99.34% F1. You can reproduce this by running the evaluation script against the held-out Zeek dataset.
```bash
python scripts/evaluate_v5.py
```
    """)

    write_file("docs/06_operations/testing_benchmarking.md", """
# Testing & Benchmarking

## T1-T15 Complete Test Guide
We validate against 15 specific network scenarios.
* **Command**: `pytest tests/test_full_regression.py`
* **Limitation**: The system successfully intercepts 11/12 malicious threats. T11 (Slow Scan) is a documented False Negative due to 10s temporal windowing.

## Performance
* **Throughput**: ~3,120 flows/sec (Containerized benchmark).
* **Latency**: ~1.40ms P50 ML Inference.
    """)

    write_file("docs/06_operations/troubleshooting.md", """
# Troubleshooting & Recovery

## Failure Recovery Matrix

```mermaid
stateDiagram-v2
    [*] --> Healthy
    Healthy --> Degraded: Component Failure
    Degraded --> Recovering: Service restart / Buffer
    Recovering --> Healthy: Recovery verified
```

* **Zeek Failure**: Adapter degrades. On restart, resumes processing trailing logs.
* **Redpanda Failure**: Adapter queues memory. At-least-once delivery guaranteed.
* **Mongo Failure**: Fusion engine retries. Duplicate-safe operations.
    """)

    write_file("docs/06_operations/hardware_deployment.md", """
# Physical Hardware Deployment

> **NOT VALIDATED**

Our current 15-stage regression suite runs on PCAPs via Docker (`END-TO-END CONTAINER` level validation). 

We have **not** validated physical deployment via SPAN/TAP/Hardware Data Diode. This requires an authorized Linux hardware lab with promiscuous interface tuning (offloading GRO/LRO).
    """)

    # 07 Governance & 08 Dossier
    write_file("docs/07_governance/model_governance.md", """
# Model Governance

## Model Lifecycle
* **SHADOW**: Model processes live data but does not emit cases.
* **EVALUATION**: Metrics are collected.
* **CANARY**: 5% of traffic routed to new model.
* **PRODUCTION**: Full deployment.

## Rollback
If a CANARY breaches SLA (latency > 10ms), the ModelRegistry automatically rolls back to the stable model version.
    """)
    
    write_file("docs/07_governance/research_library.md", """
# Research & Repository Library

Our project builds heavily upon open-source research and standard datasets.

## Datasets
* **CICIDS2017 & UNSW-NB15**: Standard intrusion sets used for training/validation.

## Tools
* **Agent-Reach**: A research-access AI layer used to explore documentation rapidly. *Agent-Reach is NOT part of the PS26145 passive network detection hot path.*
* **Zeek**: The core passive engine. (PRODUCTION)
* **Redpanda**: The streaming broker. (PRODUCTION)
    """)

    write_file("docs/08_dossier/jury_mode.md", """
# Ask the Jury Questions

**Q: Why passive?**
A: To guarantee the security tool cannot be weaponized against the production enclave.

**Q: Why XGBoost instead of Deep Learning?**
A: Network metadata is tabular. XGBoost is faster, highly accurate, and explainable, whereas Deep Learning is overkill for structured tabular arrays.

**Q: Why did V4 fail?**
A: Scapy (training) and Zeek (production) parsed network bytes differently (L2 vs L3). The semantic mismatch broke the model.

**Q: How do you detect encrypted traffic?**
A: We DO NOT decrypt. We use TLS metadata (JA3 fingerprints) combined with behavioral flow metrics (bytes, timing, directionality).
    """)

    write_file("docs/08_dossier/history_and_verdict.md", """
# History and Final Verdict

```mermaid
timeline
    title PS26145 Engineering Journey
    Phase 1 : Initial Architecture
    Phase 2 : ML Integration
    Phase 3 : Feature Parity Discovery (V4 Failure)
    Phase 4 : V5 Canonical Observation
    Phase 5 : Threat Gap Closure
    Phase 6 : Final Regression
```

## The Final Verdict

### VERIFIED
* Functional prototype
* XGBoost V5 (99.34% F1)
* Threat detection (11/12 Malicious)
* Streaming & Dashboard

### LIMITATIONS
* Slow scan (T11 FN)
* Physical hardware (Pending)
    """)

if __name__ == "__main__":
    build_part4()
    print("Part 4 Generated!")
