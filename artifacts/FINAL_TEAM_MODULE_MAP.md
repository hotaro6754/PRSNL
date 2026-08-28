# Final Team Module Map
## Implementation Work Packages

| Module | Purpose | Inputs | Outputs | Dependencies |
|--------|---------|--------|---------|--------------|
| MODULE-01 URL Engine | Lexical/statistical URL ML | URL String | Risk Score, Features | XGBoost, PhishTank |
| MODULE-02 Email Engine | Header/Body NLP | .eml file | Risk Score, extracted URLs | SpamAssassin, NLP |
| MODULE-03 SMS Engine | Short-text intent inference | String | Intent, Risk | NLP, URL Engine |
| MODULE-04 QR Engine | Decodes and analyzes payload | Image | Payload, Risk | URL Engine |
| MODULE-05 Web Sandbox | Headless DOM execution | URL | DOM, Network Trace | Playwright |
| MODULE-06 Network/PS26145 | Passive C2/Tunnel detection | PCAP/Stream | Anomalies | Zeek, Redpanda |
| MODULE-07 Threat Intel | Query external APIs | IoCs | Verdicts | VirusTotal, MISP |
| MODULE-08 ML/Data | Manages model versions | Datasets | .pkl files | Hugging Face |
| MODULE-09 Evidence | Cryptographic hashing | Raw data | Hash, Provenance | SHA256 |
| MODULE-10 Entity Graph | Canonicalization | Evidence | Graph Nodes | RedisGraph/Neo4j |
| MODULE-11 Correlation | Cross-modal linking | Graph | Attack Chain | Entity Graph |
| MODULE-12 Risk | Final decision engine | Correlation | CyberCase | All Engines |
| MODULE-13 Reporting | Converts Case to Docs | CyberCase | Quarkdown | Markdown |
| MODULE-14 Quarkdown | PDF/HTML compiler | Quarkdown | PDF/HTML | wkhtmltopdf |
| MODULE-15 Awareness | Contextual user education | Case Risk | UI/Lesson | CERT-In DB |
| MODULE-16 Security | SSRF/Rebinding blocks | Requests | Block/Allow | Playwright |
| MODULE-17 Performance | Throughput optimization | - | Metrics | Redpanda |
| MODULE-18 Resilience | Chaos recovery | - | Telemetry | Docker |
| MODULE-19 QA | Golden campaign tests | - | Test Report | PyTest |
| MODULE-20 Presentation | Pitch deck generation | Telemetry | HTML/PPTX | Reveal.js |
