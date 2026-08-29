# SOC Dashboard

## Anatomy of the SOC
Our frontend is a React-based Single Page Application connected via WebSockets.

* **Health**: Live metrics of Redpanda, Redis, and ML stages.
* **Timeline**: Real-time incoming observations.
* **Security Cases**: The fused output.

A Security Case provides an analyst with:
1. Threat Class (e.g., DDoS)
2. Severity & Confidence
3. Cryptographic Model Version (e.g., `v5-prod`)
4. Raw Evidence Matrix