# GRAFANA AUDIT
* Dashboards are strictly querying Prometheus endpoints.
* Failure Mode: If Grafana container is destroyed, CyberOS API and Browser Shield continue functioning 100%. The frontend displays "OBSERVABILITY DEGRADED".
