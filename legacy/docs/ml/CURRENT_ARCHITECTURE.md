# Current Architecture State

## Overview
The system is currently a validated, deterministic, passive Network Detection and Response (NDR) platform operating under strict Zero-Slop Execution boundaries. 

## Data Plane & Ingestion
- **PCAP / Offline**: Ingestion is currently bottlenecked (~170 flows/sec) due to synchronous Scapy parsing in `ScapyAdapter`.
- **Streaming Pipeline**: `ZeekAdapter` and `KafkaObservationProducer/Consumer` have been staged (P1) but are waiting on Redpanda deployment.

## Contract Layer
- Pydantic models define the ecosystem: `NetworkObservation`, `DetectionEvidence`, `FeatureVector`, `MLPrediction`, `Alert`, and `SecurityCase`.
- Observations explicitly preserve the PCAP/sensor `timestamp` (event time), decoupling logic from processing time.

## Detection Engine
- **Deterministic**: Heuristic modules operate on stateful tumbling windows (using Coefficient of Variation and Shannon Entropy).
  - Active: DDoS, PortScan, Beaconing, DGA, DNS Tunnelling, TLS Anomalies, Exfiltration.
- **AI/ML State**: There are legacy `.pkl` files (`ddos_model.pkl`, `dga_model.pkl`) trained on randomly generated synthetic numpy distributions using Isolation Forests. These are strictly placeholder/synthetic and are NOT real models.

## Correlation & Persistence
- Alerts flow into the `CorrelationEngine`, rolling up into `SecurityCase`.
- `MongoRepository` is stubbed as the persistence boundary for Cases and Alerts, decoupled from the high-speed data plane.
- Next.js / shadcn UI visualizes these cases.
