# PHASE 6 GAP REGISTER

| ID | Component | Current Status | Why Incomplete / Notes | PS#5 Relevance | Production Impact | Priority |
|----|-----------|----------------|------------------------|----------------|-------------------|----------|
| GAP-001 | Redpanda Deployment | REAL CONTAINERIZED | Misclassified as simulation previously. It runs in Docker. | Zeek Telemetry | LOW | LOW |
| GAP-002 | Zeek Deployment | REAL CONTAINERIZED | Runs in Docker container, ingesting real PCAPs. | Network Telemetry | LOW | LOW |
| GAP-003 | Playwright SSRF | PARTIAL | Browser Sandbox lacks DNS rebinding protection & IP validation. | Web Pages | CRITICAL | BLOCKER |
| GAP-004 | SMS ML Engine | PARTIAL | Relies on regex heuristics; lacks a trained intent model. | SMS Analysis | HIGH | HIGH |
| GAP-005 | QR Image Decoder | PARTIAL | Fails on rotated/noisy QR codes; lacks structural features. | QR Codes | MEDIUM | MEDIUM |
| GAP-006 | Social Media Ingestion | NOT IMPLEMENTED | No platform API connectors. Moving to User-Submitted text path. | Social Media | LOW | MEDIUM |
