# PS26145 Enterprise Regression Matrix

| ID | Scenario | Category | Expected | Observed | Status |
|---|---|---|---|---|---|
| E01 | Normal Enterprise Baseline | baseline | CLEAN | CLEAN | PASS |
| E02 | High-Volume Benign Burst | load | CLEAN | CLEAN | PASS |
| E03 | High-Fanout Enterprise CDN Pattern | baseline | CLEAN | CLEAN | PASS |
| E04 | Simultaneous Threat Mix | threat_mix | INDEPENDENT_DETECTIONS | INDEPENDENT_DETECTIONS | PASS |
| E05 | Multi-Host Incident | threat_mix | ENTITY_SPECIFIC_CASES | ENTITY_SPECIFIC_CASES | PASS |
| E16 | ML WORKER FAILURE | chaos | DEGRADED_BUT_DETERMINISTIC_WORKS | DEGRADED_BUT_DETERMINISTIC_WORKS | PASS |
| E18 | REDPANDA FAILURE | chaos | RECOVERED_AT_LEAST_ONCE | RECOVERED_AT_LEAST_ONCE | PASS |
| E20 | MONGODB FAILURE | chaos | BUFFERED_AND_RECOVERED | BUFFERED_AND_RECOVERED | PASS |
| E36 | MIXED ATTACK + FAILURE CHAOS | havoc | PARTIAL_DETECTION_NO_CRASH | PARTIAL_DETECTION_NO_CRASH | PASS |
