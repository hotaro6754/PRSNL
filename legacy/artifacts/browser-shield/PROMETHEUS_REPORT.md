# PROMETHEUS VALIDATION
* The `/metrics` endpoint correctly exposes `ml_inferences_total`, `ndr_flows_processed_total`, and `cyberos_alerts_generated_total`.
* I verified that stopping browser activity causes these counters to flatline precisely.
* I verified that triggering a browser event cleanly steps the counter by +1.
