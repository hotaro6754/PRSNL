# THREAT MODEL

## Defenses
- **Malicious Webpages**: The extension UI runs in an isolated context (`chrome-extension://`). Content scripts are not used for rendering sensitive security decisions to prevent DOM clobbering.
- **Message Spoofing**: All communication relies on standard Extension APIs which enforce origin checks. 
- **SSRF / Token Theft**: The CyberOS API bridge utilizes explicit fetch policies.
