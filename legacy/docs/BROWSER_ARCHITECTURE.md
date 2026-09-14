# BROWSER ARCHITECTURE

CyberOS employs Chromium (via Playwright) isolated in Docker containers for Web Threat Detection.

## Workflow
1. Request arrives.
2. Tenant Quota Check.
3. SSRF pre-resolution on Target URL.
4. Chromium Headless boots.
5. Navigation bounds applied (domcontentloaded, 8s timeout).
6. DOM traversal and evidence generation.
7. Chromium context destroyed to prevent state contamination.

We explicitly rejected lightweight parsers (Lightpanda) due to their inability to trigger native V8 execution flows mandatory for uncovering dynamic Javascript obfuscation and Canvas fingerprinting attacks.
