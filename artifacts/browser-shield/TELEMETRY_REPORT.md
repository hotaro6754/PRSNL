# TELEMETRY ARCHITECTURE
**Principle:** 1 Real Event = 1 Metric Increment.
* The frontend `setInterval(fetchData, 5000)` strictly pulls *real* counters from the API.
* Fake `random.randint()` simulated heartbeats were completely eradicated from the `metrics_snapshot_task`.
* When the UI displays "0 EPS" or "0 Active Investigations", it is the factual truth of the system state.
