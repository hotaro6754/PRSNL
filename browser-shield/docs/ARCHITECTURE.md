# BROWSER SHIELD ARCHITECTURE

## Core Philosophy
The extension is the **CLIENT**. CyberOS remains the **SECURITY BRAIN**. The browser does not duplicate the risk engine, graph, or full threat intelligence database. 

## Component Flow
```mermaid
graph TD
    A[Browser Navigation] --> B[Background Service Worker]
    B --> C{Local Whitelist/Cache}
    C -->|Hit| D[Allow Navigation]
    C -->|Miss| E[CyberOS API Bridge POST /api/scan]
    E --> F{CyberOS Backend Risk Engine}
    F -->|SAFE| G[Store Verdict -> Allow]
    F -->|HIGH RISK| H[Intercept Navigation]
    H --> I[Warning Interstitial /warning.html]
    I --> J[Investigate / Case Creation]
```

## Progressive Analysis
1. **Phase 1 (ms)**: Local caching.
2. **Phase 2 (fast)**: API bridge to CyberOS `scan` endpoint.
3. **Phase 3 (deep)**: CyberOS fetches Threat Intel, local XGBoost evaluation, and correlates evidence.
