# FAILURE MODE VALIDATION
* **Backend DOWN:** Extension fails open. User browses normally. Status: LIMITED PROTECTION.
* **ML Worker DOWN:** Backend falls back to Threat Intelligence & Heuristics. Status: DEGRADED.
* **Grafana DOWN:** Dashboard shows UI errors on graphs, but detection pipelines remain 100% operational.
