# Redis Entity Behavior

## Bounded State
Stateless processing is impossible for behavioral detection. A port scan takes time. A beacon takes time. 
However, storing indefinite state in RAM causes Out Of Memory (OOM) crashes.

We use **Redis** to maintain host behavioral baselines with strict Time-To-Live (TTL) expirations. If a host isn't seen for 5 minutes, its baseline gracefully expires.