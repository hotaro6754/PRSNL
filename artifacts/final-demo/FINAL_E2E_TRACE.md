# FINAL E2E GOLDEN SCENARIO TRACE
1. **Encounter**: User navigates to `http://evil.com/login`
2. **Intercept**: Browser Shield detects `status: complete`.
3. **API Bridge**: `POST /api/scan` triggered with JWT header.
4. **Analysis**: `cyberos-ml-worker` computes XGBoost matrix. Threat Intel API queried.
5. **Entity Graph**: `evil.com` mapped to IP `192.168.100.50` in MongoDB.
6. **Risk Engine**: Evidence aggregated via Probabilistic OR. Score: 95.
7. **Protection**: Interstitial Warning blocks DOM.
8. **Provenance**: "PROVE THIS" reveals `CASE_ID`, Detector, Timestamp.
9. **Investigation**: "INVESTIGATE" deep-links to `/cases/CYB-991`.
10. **Telemetry**: `ndr_flows_processed_total` += 1 mapped in Grafana.
