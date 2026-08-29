# E2E PROTECTION SCENARIO
**Test**: User visits `http://evil.com/login` (Phishing site)
1. Browser loads page.
2. Extension background worker observes navigation completion.
3. Pre-check misses (not in whitelist).
4. API call made to `http://localhost:8000/api/scan`.
5. Backend invokes XGBoost URL model -> Score 0.95.
6. Backend responds with `CRITICAL`.
7. Worker redirects to `chrome-extension://[id]/warning.html`.
8. Interstitial displays "HIGH RISK" with evidence bullet points.
**Result**: PASSED (Post-navigation).
