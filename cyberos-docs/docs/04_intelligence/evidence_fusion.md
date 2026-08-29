# Evidence Fusion

```mermaid
flowchart LR
    A[NetworkObservation] --> B[Rules]
    A --> C[XGBoost]
    B --> D[Fusion Engine]
    C --> D
    D --> E[SecurityCase]
```

## Why Fusion?
A single anomaly detection model will inevitably trigger False Positives. Our **Fusion Engine** demands cross-validation. An XGBoost alert will not become a severe Security Case unless deterministic logic provides contextual evidence (e.g., high probability + high exfiltration ratio).