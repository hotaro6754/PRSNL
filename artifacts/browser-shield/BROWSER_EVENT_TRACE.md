# BROWSER EVENT TRACE
**Golden Scenario Execution Trace**
* **Timestamp**: 2026-08-29T14:02:00Z
* **Event ID**: `evt_9a8b7c`
* **URL**: `http://evil.com/login`
1. **Browser**: `chrome.tabs.onUpdated` triggered (status: complete).
2. **Pre-check**: Miss (Domain not in whitelist).
3. **CyberOS Request**: `POST /api/scan` dispatched with Bearer JWT.
4. **Analysis**: 
   - XGBoost Model `URL_SECURITY_v2` computed `0.95`.
   - Threat Intelligence checked (No external match).
5. **Database**: CyberCase `CYB-12345` created. Evidence records persisted to MongoDB.
6. **Response**: Risk 95, Classification `CRITICAL`.
7. **Warning Intercept**: Browser redirects tab to `chrome-extension://[id]/warning.html?case_id=CYB-12345`.
8. **Prometheus Observation**: `ndr_flows_processed_total` incremented by 1. `cyberos_alerts_generated_total` incremented by 1.
9. **Grafana Observation**: Peak registers on the timeline graph for 14:02:00Z.
