# BROWSER EXTENSION SECURITY
* **XSS**: React renders evidence safely.
* **Token Leakage**: JWT stored in `chrome.storage.local`.
* **Tenant Isolation**: Backend enforces RBAC on `case_id` lookup.
* **SSRF**: Backend Playwright sandbox isolates URL scans.
