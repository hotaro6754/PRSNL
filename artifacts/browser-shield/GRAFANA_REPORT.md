# GRAFANA CONFIGURATION
* **Datasource:** Provisioned natively via Prometheus HTTP target.
* **Dashboards:** Stored in source control. Survives `docker compose down -v`.
* **Resilience:** If Grafana container dies, the browser extension and CyberOS API continue functioning unimpeded. The frontend dashboard fails gracefully to "OBSERVABILITY DEGRADED".
