# Sentinel-26145 design

## 1. What the sensor sees, and what "one-way" means

The monitored link (gateway or peering link) is copied into the monitoring enclave by a passive tap, SPAN port or hardware data diode. The copy carries **both directions of the monitored traffic**; what is one-way is the enclave's connection to production — the enclave can receive, never transmit back. So:

* Reverse-direction evidence (SYN-ACKs, DNS responses, server byte counts) is used when it is present.
* It is never *assumed*. Taps drop packets without notice (a UDP diode cannot ask for retransmission), and asymmetric routing means some flows are seen in one direction only. Every alert therefore records the visibility it was produced under (section 4).
* Nothing in the sensor sends a packet, completes a handshake, resolves a name or queries a live service. Intelligence (popular-domain list, JA3 blocklist, DGA model) is loaded from files inside the enclave.

## 2. Pipeline

```
capture file / pcap stream on stdin (tcpdump -w -)
      │  streaming reader: SHA-256 of the input, byte offset of every packet
      ▼
FlowMeter  (sentinel/ingest/flowmeter.py)
  • bidirectional flow table, Community ID v1, TCP state, per-direction TCP sequence tracking (loss)
  • TLS ClientHello / ServerHello reassembly → JA3, JA4, JA3S, SNI, ALPN, negotiated version
  • DNS query/response matching → name, type, rcode, answers (or "no response seen")
  • per-destination one-second aggregates (SYNs, SYN-ACKs sent, UDP, amplification-port bytes, source table)
  • timers: failed attempt 5 s, idle 60 s TCP / 30 s UDP, active timeout 60 s (long flows exported incrementally)
      │  events: FlowRecord · DnsEvent · TlsEvent · DstSecond
      ▼
Detectors (sentinel/detect/*)  — all run on every event, in-process, bounded state
      ▼
Store (SQLite, append-only) → SHA-256 hash chain + Ed25519 signature per alert
      ▼
Case correlator → cases        API (FastAPI) → SSE stream → dashboard
```

Processing is event-driven and incremental: an alert is raised while the traffic is still being read (PS constraint c). The evaluation report measures detection delay from attack start (event time) and processing latency per event.

## 3. Detection methods (PS categories a–f)

| PS | Class | Method | Main evidence fields |
|----|-------|--------|----------------------|
| a | `ddos.syn_flood` | Per-destination second aggregates; SYN rate ≥ 400/s, handshake completion ≤ 20 % **or** ≥ 200 sources with normalised source entropy ≥ 0.85 (spoofed), above the destination's learned baseline, sustained 3 s | syn_per_second, unique_sources, source_entropy_normalised, handshake_completion_ratio |
| a | `ddos.udp_amplification` | UDP from amplification service ports (DNS, NTP, SSDP, memcached, CLDAP…) toward one host: ≥ 4 Mbit/s, ≥ 30 reflectors, mean response ≥ 300 B, < 10 % matching requests from the target | amplified_traffic, reflectors, mean_response_size, requests_sent_by_target |
| a | `ddos.udp_flood` | UDP packet rate ≥ 3000/s and 8× the destination baseline, sustained | udp_packets_per_second, source entropy |
| b | `c2.beaconing` | Per (internal host, external destination, port): connection start intervals scored with Bowley skew and median absolute deviation (robust to jitter and missed beacons), request-size regularity and persistence (RITA-style score ≥ 0.80, ≥ 8 connections). Destinations polled by ≥ 5 internal hosts are downgraded (update / telemetry services) | median_interval, jitter %, interval skew, request size dispersion, beacon_score |
| c | `dns.dga` | Character 1–4-gram logistic regression on the registrable label, isotonic-calibrated; needs ≥ 6 distinct high-probability (≥ 0.90) domains from one host in 10 min; popular domains skipped | distinct domains, mean probability, NXDOMAIN ratio, examples |
| c | `dns.tunnel` | Per (host, registered domain) in 120 s: ≥ 40 unique subdomains, ≥ 2500 encoded characters, long labels (mean ≥ 18) or high character entropy (≥ 3.3 bits); TXT/NULL/CNAME/MX share as supporting evidence | unique_subdomains, label length, entropy, estimated upstream rate, record types |
| d | `tls.known_bad_fingerprint` | JA3 match against the abuse.ch SSLBL snapshot (historical list, reported as evidence, not verdict) | tls_ja3, listing reason |
| d | `tls.suspicious_session` | JA4 client fingerprint used by ≤ 2 internal hosts, repeated ≥ 5 sessions to one external destination with no SNI / IP-literal SNI or an unranked registered domain. Handshake metadata only; payload is never inspected | tls_ja4, hosts using fingerprint, sni, indicators |
| e | `recon.scan` | Threshold Random Walk sequential test over first-contact connection outcomes (α = 0.01, β = 0.99); fan-out fallback (≥ 50 ports on a host / ≥ 50 hosts on a port) with failure ratio; disabled-with-explanation when TCP replies are not visible | TRW log-likelihood ratio, distinct targets, failure ratio, services that answered |
| f | `exfil.volume` | Per (internal host, external destination) 10-minute window of flow byte increments: ≥ 20 MB out, out/in ratio ≥ 8, and ≥ 4σ above the host's own EWMA outbound baseline; sanctioned destinations allow-listed. With one-way visibility only very large volumes alert, at confidence 0.35 | outbound/inbound bytes, ratio, rate, host baseline z |

All thresholds live in `sentinel/config.py` and appear in each alert's evidence (`threshold`, `baseline`), so an analyst can see exactly why it fired.

### Why these models

* **Rules and statistics where the behaviour is defined by protocol arithmetic** (floods, amplification, scanning, volume). They are exact, explainable and need no training data that would not transfer between networks.
* **A learned model where rules generalise poorly**: DGA names. A linear model over hashed character n-grams is small (256k weights), sub-millisecond, calibrated, and loads without pickle.
* **No deep models or LLMs in the detection path.** They add latency, are hard to justify to an analyst, and attacker-controlled strings (DNS names, SNI) would become prompt-injection input.

### DGA model training and validation (`ml/train_dga.py`)

* Malicious: 30 796 domains from 39 reverse-engineered DGA families (`ml/collect_dga.py`).
* Benign: Tranco top-1M.
* Splits are **by family** (10 families never seen in training) and **by popularity rank** (train on ranks ≤ 400k, test on 400k–1M — unpopular real names look most like DGA output). No random row split.
* Calibration: isotonic regression on a validation split.
* Results are recorded in `models/dga/dga_char_ngram_lr.json` and shown on the Evaluation page. On held-out families at the operating threshold 0.9: precision 0.938, recall 0.500, per-domain false-positive rate 0.31 %, ROC-AUC 0.854. Random-character families are caught well (sisron 98 %, zloader 92 %, banjori 87 %); dictionary-word families are largely missed (simda 8 %, nymaim2 0 %). The host-level burst requirement and top-list exclusion reduce false alerts beyond the per-domain rate.

## 4. Visibility

Each alert carries:

```json
"visibility": {"directions_seen": 2.0, "handshake_seen": true, "est_loss_pct": 0.4, "sufficient": true, "note": null}
```

* `directions_seen` — mean directions observed per contributing flow.
* `est_loss_pct` — bytes missing according to TCP sequence numbers, as a share of the bytes that should have been seen.
* `sufficient` — false when the method needs evidence the tap did not deliver (e.g. an exfiltration ratio with no reverse direction, a scan outcome test with no replies). Confidence is reduced and `note` says why.

## 5. Custody

* The input capture is SHA-256 hashed while it is read; every packet keeps its byte offset.
* Each alert records the capture hash, packet pointers and an evidence scope (hosts, ports, protocol, time and offset range).
* Alerts are appended to SQLite with triggers refusing UPDATE/DELETE, and chained: `hash_n = SHA-256("n:hash_(n-1):" ‖ canonical JSON)`, signed with the sensor's Ed25519 key.
* `GET /api/alerts/{id}/bundle` (or `python -m sentinel bundle`) produces a zip with the alert, the supporting packets cut from the original capture, the manifest of SHA-256 values, the public key and a technical annex listing the hash facts a certificate under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 asks for.
* `python -m sentinel verify-bundle` checks the bundle offline and, given the original capture, re-extracts the packets and compares them byte for byte. Tests cover modified captures, edited alerts and a bypassed trigger.

## 6. Threat model of the sensor itself

| Threat | Control |
|--------|---------|
| Parser exploitation by hostile traffic | Pure-Python parsers with bounds checks; malformed input is counted and skipped; container runs unprivileged, read-only root, all capabilities dropped |
| Sensor used as a pivot | No transmit path in code; capture happens outside the container (tcpdump receive-only); API bound to localhost in compose |
| Unauthorised control | Analyst and admin bearer tokens; control endpoints admin-only; constant-time comparison |
| Path traversal / arbitrary file read | Captures only by name from one directory, name pattern-checked, resolved path must stay inside it |
| Evidence tampering | Append-only triggers, hash chain, Ed25519 signatures, capture hash, offline bundle verification |
| Malicious model artefact | Model is `.npz` loaded with `allow_pickle=False`; SHA-256 recorded in every model-based alert |
| XSS via traffic strings | Dashboard renders DNS names / SNI as text only (React escaping); no HTML injection |
| Resource exhaustion by spoofed floods | Bounded per-key state, capped source tables per second, flow table eviction, cooldowns |

## 7. Known limits

* Throughput is single-core Python: 1 000 flows/s (≈ 11 000 packets/s) sustained on the measured host, failing at 1 500 flows/s (`results/benchmark.json`). Multi-gigabit links need several sensor processes behind a flow-hash split (AF_PACKET fan-out or a Zeek front end); not implemented.
* Beaconing needs at least 8 check-ins, so slow beacons are detected late (delay ≈ 7 × interval).
* TLS 1.3 with encrypted ClientHello or QUIC hides SNI; JA4 still identifies the client stack, and the TLS detector's no-SNI indicator becomes weaker.
* DNS over HTTPS removes DNS visibility entirely; the DNS detectors then see nothing.
* The published evaluation uses a synthetic labelled capture. It demonstrates end-to-end behaviour and bounds false alerts on that background; real-network validation (e.g. CTU-13, operator captures) is the next step.
