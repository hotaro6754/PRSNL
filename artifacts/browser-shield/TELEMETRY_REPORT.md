# TELEMETRY VALIDATION
* **System Telemetry**: Backend explicitly simulates 30-80 EPS network traffic using Prometheus metrics (`FLOWS_PROCESSED`).
* **Grafana Integration**: Grafana actively scrapes `backend:8000/metrics`.
* **Browser Metrics**: **PARTIAL**. The API tracks `/api/scan` counts, but distinct browser vs UI scans are not strongly partitioned in Prometheus yet.
