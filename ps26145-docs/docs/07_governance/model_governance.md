# Model Governance

## Model Lifecycle
* **SHADOW**: Model processes live data but does not emit cases.
* **EVALUATION**: Metrics are collected.
* **CANARY**: 5% of traffic routed to new model.
* **PRODUCTION**: Full deployment.

## Rollback
If a CANARY breaches SLA (latency > 10ms), the ModelRegistry automatically rolls back to the stable model version.