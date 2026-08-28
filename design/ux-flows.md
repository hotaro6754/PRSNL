# UX FLOWS
## THE GOLDEN DEMO FLOW (AITAM Hacksprint)
1. **Input:** User submits SMS/URL.
2. **Analysis Spinner:** System extracts indicators, ML inferencing, Web Sandboxing. No fake loading bars.
3. **Evidence View:** Real timestamped logs (e.g. 14:32:11 SMS submitted). 
4. **Entity Graph:** Mermaid-powered interactive graph. MESSAGE -> URL -> DOMAIN -> IP -> WEB -> NETWORK.
5. **Risk & Why:** Risk Engine outputs CRITICAL. Clicking 'Why?' shows exact Evidence contributions, not AI prose.
6. **Action & Report:** Recommended action (Do not click). 'Generate Report' fires Quarkdown pipeline.
7. **Education:** Contextual Quishing/Smishing module displayed.
