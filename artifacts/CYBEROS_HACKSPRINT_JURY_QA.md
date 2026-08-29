# CYBEROS — HACKSPRINT JURY Q&A DEFENSE

### Q1: Why is this PS#5?
**Answer:** PS#5 explicitly asks for a system to identify suspicious digital content (URLs, Emails, SMS, QR, Web) and explain the risks. CyberOS implements engines for every required modality and outputs Quarkdown reports and CERT-In education modules. 

### Q2: Why not just use VirusTotal?
**Answer:** VirusTotal provides reputation intelligence, but it does not observe live DOM execution, it does not correlate cross-modal attacks (e.g., an SMS leading to a DNS tunnel), and it does not educate the user. CyberOS uses VT as an enrichment layer, not the final verdict.

### Q3: Why not ChatGPT?
**Answer:** LLMs hallucinate. CyberOS is deterministic security instrumentation. It relies on cryptographic evidence provenance, real network telemetry (Zeek/Redpanda), and isolated Web DOM sandboxing. 

### Q4: What happens if the QR code is unreadable?
**Answer:** The system degrades safely. Test QR-010 proves that if the payload is obscured, the Risk Engine outputs UNVERIFIED rather than hallucinating a malicious or benign classification.

### Q5: How do you prevent SSRF in the Web Sandbox?
**Answer:** The Playwright container is restricted. Test WEB-SSRF-009 proves we block IPv4-mapped IPv6 loopbacks, DNS rebinding, and metadata IP access.
