# SOC and NDR

## What is a SOC?
A **Security Operations Center (SOC)** is the facility where an organization's security team monitors and analyzes the security posture. 

```mermaid
flowchart LR
    A[Network Event] --> B[Detection]
    B --> C[Alert]
    C --> D[Correlation]
    D --> E[Security Case]
    E --> F[SOC Analyst]
```

## What is NDR?
**Network Detection and Response (NDR)** analyzes raw network traffic to detect threats. 

| Technology | Sees Network | Active Response | Primary Purpose |
| ---------- | ------------ | --------------- | --------------- |
| **NIDS** | Yes | No | Detect threats (signature based) |
| **IPS** | Yes | Yes | Block threats inline |
| **SIEM** | No (Uses Logs) | No | Log aggregation & alerting |
| **NDR** | Yes | Yes (via integration) | Behavioral ML threat detection |

PS26145 is a purely passive NDR solution.