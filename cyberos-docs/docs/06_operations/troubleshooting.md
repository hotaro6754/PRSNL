# Troubleshooting & Recovery

## Failure Recovery Matrix

```mermaid
stateDiagram-v2
    [*] --> Healthy
    Healthy --> Degraded: Component Failure
    Degraded --> Recovering: Service restart / Buffer
    Recovering --> Healthy: Recovery verified
```

* **Zeek Failure**: Adapter degrades. On restart, resumes processing trailing logs.
* **Redpanda Failure**: Adapter queues memory. At-least-once delivery guaranteed.
* **Mongo Failure**: Fusion engine retries. Duplicate-safe operations.