import os

docs_dir = "E:\\sih26145-prototype\\browser-shield\\docs"
os.makedirs(docs_dir, exist_ok=True)

docs = {
    "BROWSER_SHIELD.md": """# CYBEROS BROWSER SHIELD
**REAL-TIME WEB PROTECTION + CYBEROS INTELLIGENCE FABRIC**

## Overview
CyberOS Browser Shield is a browser-native protection layer that continuously evaluates the pages and navigation events a user encounters and connects them to the existing CyberOS security intelligence platform.

It transforms CyberOS from a reactive "submit something" platform into a proactive, real-time protection shield.

## Capabilities
- **Fast Local Pre-Check**: Instantly resolves known safe domains via local caching to reduce latency.
- **Progressive Risk Analysis**: Calls the authoritative CyberOS ML/Intelligence backend API for unverified URLs.
- **Safe / Review / Blocked**: Intercepts dangerous navigation with a high-fidelity warning interstitial.
- **Explainability**: Every warning provides the exact evidence chain ("Why CyberOS Warned You").
- **Direct Investigation**: "Investigate in CyberOS" routes the threat into the Security Operations Center queue.
""",

    "ARCHITECTURE.md": """# BROWSER SHIELD ARCHITECTURE

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
""",

    "PRIVACY.md": """# PRIVACY POLICY

## Principle
Collect only what CyberOS actually needs.

## Data Collection
- **Collected**: Destination URLs, origin, and transition type.
- **NOT Collected**: Passwords, form submissions, authentication cookies, credit card numbers, private messages, or unrelated browsing history.

## Modes
- **LOCAL-FIRST**: Checks local heuristics and cache before querying the backend.
- **ENTERPRISE**: Follows strict organization data-retention policies as defined in the CyberOS platform.
""",

    "SECURITY.md": """# SECURITY ARCHITECTURE

## Permissions (Manifest V3)
- `tabs`: Required to monitor and intercept high-risk navigation.
- `storage`: Required for local policy caching and verdict state management.
- `activeTab`: Required for popup interactions.
- `host_permissions: ["http://localhost:8000/*"]`: Restricts backend API calls explicitly to the CyberOS instance.

## Offline / Degraded Mode
If the CyberOS backend is unavailable, the extension degrades gracefully. It will display a "LIMITED PROTECTION" state rather than claiming "SAFE".
""",

    "THREAT_MODEL.md": """# THREAT MODEL

## Defenses
- **Malicious Webpages**: The extension UI runs in an isolated context (`chrome-extension://`). Content scripts are not used for rendering sensitive security decisions to prevent DOM clobbering.
- **Message Spoofing**: All communication relies on standard Extension APIs which enforce origin checks. 
- **SSRF / Token Theft**: The CyberOS API bridge utilizes explicit fetch policies.
""",

    "DEPLOYMENT.md": """# DEPLOYMENT GUIDE

## Development Build
```bash
npm run dev
```
Loads the extension into Chrome via WXT.

## Production Build
```bash
npm run build
```
Generates the `.zip` archive for the Chrome Web Store and Enterprise Policy deployment.
"""
}

for name, content in docs.items():
    with open(os.path.join(docs_dir, name), "w", encoding="utf-8") as f:
        f.write(content)

print("Generated documentation.")
