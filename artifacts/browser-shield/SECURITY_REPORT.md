# SECURITY VALIDATION
* **XSS**: Warning page strictly parses evidence via `JSON.parse` and maps to structured components. React escapes content natively.
* **Origin Spoofing**: Backend API is exposed to `localhost`. CSRF is mitigated if CORS is strictly configured, but currently unauthenticated.
* **SSRF**: Backend `analyze_url` uses Playwright and `urllib`. Must be strictly isolated.
