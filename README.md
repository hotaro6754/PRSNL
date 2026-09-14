# Sentinel-26145

Passive threat detection for one-way IP traffic — Smart India Hackathon problem statement **26145** (National Technical Research Organisation).

Sentinel reads a copy of a gateway or peering link (packet capture, or a live capture stream from a tap / data-diode receive interface) and raises structured, evidence-backed alerts for the six threat categories in the problem statement. It never transmits toward the monitored network, never decrypts payload, and processes traffic as a stream. Each alert is sealed into a signed hash chain and can be exported with the exact packets that support it.

## What is in this repository

| Path | Contents |
|------|----------|
| `sentinel/` | detection engine: capture reader, flow meter (TCP state, TLS JA3/JA4, DNS), detectors, case correlation, signed alert store, evidence bundles, API, CLI |
| `ml/` | DGA data collection, training and evaluation; end-to-end evaluation and throughput benchmark |
| `models/dga/` | trained DGA model (`.npz`, no pickle) and its manifest with test metrics |
| `lab/` | labelled lab traffic generator (`python -m sentinel.lab.generate`) |
| `results/` | measured evaluation and benchmark reports (read by the dashboard) |
| `frontend/` | analyst dashboard (Next.js) |
| `deploy/` | container images and compose file for an enclave deployment |
| `docs/DESIGN.md` | design, detection methods, custody, threat model, limits |
| `docs/alert.schema.json` | JSON Schema of the alert record |
| `tests/` | unit, detector, custody, evidence-bundle and API tests |
| `legacy/` | the previous prototype, kept for reference; not used |

## Problem statement coverage

| PS requirement | How it is met | Where to check |
|----------------|---------------|----------------|
| (a) Volumetric / protocol DDoS | per-destination second aggregates: SYN rate, handshake completion, source cardinality and entropy (spoofed floods); UDP amplification from reflector service ports; UDP floods against a learned baseline | `sentinel/detect/ddos.py` |
| (b) C2 beaconing | interval regularity (Bowley skew, median absolute deviation), request-size regularity, persistence; fleet-wide polling downgraded | `sentinel/detect/beacon.py` |
| (c) DGA and DNS tunnelling | character n-gram model (calibrated) with a per-host burst rule; tunnelling from unique subdomains, label length, entropy, encoded volume and record types | `sentinel/detect/dns.py`, `ml/train_dga.py` |
| (d) Malware in encrypted sessions | TLS handshake metadata only: JA4/JA3, SNI, ALPN, version; rare client fingerprints repeatedly contacting unranked or IP-literal destinations; offline JA3 blocklist | `sentinel/detect/tls.py`, `sentinel/proto/tls.py` |
| (e) Reconnaissance and scanning | Threshold Random Walk sequential test on connection outcomes, plus fan-out | `sentinel/detect/scan.py` |
| (f) Data exfiltration | outbound/inbound byte asymmetry per host and destination, against each host's own outbound baseline; visibility-checked | `sentinel/detect/exfil.py` |
| Read-only ingest | reads files or a pcap stream on stdin; no socket toward monitored traffic anywhere in `sentinel/`; container has all capabilities dropped | `sentinel/ingest/pcapio.py`, `deploy/` |
| No payload decryption | only cleartext handshake fields are parsed | `sentinel/proto/tls.py` |
| Streaming, not batch | packet-by-packet flow meter with timers; alerts raised while traffic is read; detection delay reported per class | `sentinel/ingest/flowmeter.py`, `results/evaluation.json` |
| Defined throughput target | measured steady-rate ladder, stated below | `ml/benchmark.py`, `results/benchmark.json` |
| Standardised alert schema | versioned `sentinel.alert/1.0` record: timestamps, Community ID flow IDs, class, ATT&CK technique, confidence, evidence with thresholds and baselines, visibility, model hash, custody | `sentinel/alerts.py`, `docs/alert.schema.json` |

## Measured results

All figures below come from `results/*.json` and `models/dga/*.json`, produced by the scripts named. Host: Intel Core (12 logical CPUs), Windows 11, Python 3.14, **one process on one core**, all detectors enabled, every alert signed and persisted.

### Throughput (constraint d)

`python ml/benchmark.py lab/captures/lab-30m.pcap --rates 500 1000 1500 2000 3000 --seconds 20`

Uniform benign sessions (DNS lookup, TCP handshake, TLS ClientHello on one session in five, request/response, close) released against the wall clock. Sustained = p99 packet lag < 0.5 s and lag at end < 1 s.

| Offered flows/s | Packets/s | Lag p99 | Sustained |
|---:|---:|---:|:--|
| 500 | 5 580 | 0.05 s | yes |
| **1 000** | **11 159** | **0.21 s** | **yes** |
| 1 500 | 16 739 | 2.84 s | no |
| 2 000 | 22 318 | 10.4 s | no |

**Stated target: 1 000 flows/s (≈ 11 000 packets/s) sustained on a single core.** Unpaced, the pipeline processed the 30-minute lab capture at 23 095 packets/s (1 389 flows/s, 247 Mbit/s of original traffic). Per-event detection work: p50 0.06 ms, p99 0.24 ms. Higher link rates need several sensor processes behind a flow-hash split; that is not implemented here.

### Detection on a labelled lab capture

`python -m sentinel.lab.generate --hours 2` then `python ml/evaluate.py lab/captures/lab-2h.pcap`

2 hours, 2.58 million packets: 60 hosts browsing over TLS, DNS, NTP, fleet-wide update polling every 30 minutes, large downloads, a sanctioned backup upload and a monitoring poller, with 9 labelled attacks injected.

| Class | Detected | False alerts | Delay from attack start |
|-------|:--:|:--:|--:|
| ddos.syn_flood (spoofed) | 1 / 1 | 0 | 3.0 s |
| ddos.udp_amplification | 1 / 1 | 0 | 3.0 s |
| recon.scan | 1 / 1 | 0 | 0.04 s |
| exfil.volume | 1 / 1 | 0 | 1.9 s |
| dns.tunnel | 1 / 1 | 0 | 8.8 s |
| dns.dga (unseen family) | 1 / 1 | 0 | 25 s |
| tls.suspicious_session | 2 / 2 | 0 | 87 s, 235 s |
| c2.beaconing (60 s ± 15 % jitter) | 1 / 1 | 0 | 611 s |

Custody chain verified over all 11 alerts.

**This capture is synthetic.** It shows the pipeline working end to end and that it stays quiet on this benign background; it is not evidence of accuracy on real networks. The beacon delay is by design: the detector waits for 8 check-ins.

### DGA model (`ml/train_dga.py`)

Trained on 26 DGA families and Tranco ranks 1–400k; tested on **10 families never seen in training** and Tranco ranks 400k–1M.

| Threshold | Precision | Recall | False-positive rate per domain |
|--:|--:|--:|--:|
| 0.5 | 0.777 | 0.679 | 1.85 % |
| 0.9 (used) | 0.938 | 0.500 | 0.31 % |
| 0.95 | 0.963 | 0.352 | 0.13 % |

ROC-AUC 0.854. Random-character families are caught well (sisron 98 %, zloader 92 %, banjori 87 %, qakbot 77 % at 0.9); dictionary-word families are not (simda 8 %, nymaim2 0 %). The detector only alerts when one host looks up 6 or more such domains within 10 minutes, and skips the top-100k domains.

## Run it

Requirements: Python 3.11+, Node 22 for the dashboard.

```bash
pip install -r requirements-dev.txt
python -m pytest -q tests
```

Analyse a capture from the command line:

```bash
python -m sentinel.lab.generate --out lab/captures/lab-30m.pcap --hours 0.5
python -m sentinel analyze lab/captures/lab-30m.pcap
python -m sentinel verify-chain
python -m sentinel bundle <alert_id> -o evidence.zip
python -m sentinel verify-bundle evidence.zip --capture lab/captures/lab-30m.pcap
```

Live capture on a sensor host (tcpdump only receives):

```bash
sudo tcpdump -i eth1 -U -s 0 -w - | python -m sentinel analyze - --live
```

API and dashboard for local development:

```bash
python deploy/dev_api.py
cd frontend && npm ci && npx next build && npx next start -p 3000
```

The admin token for starting replays is written to `var/admin_token`; enter it on the dashboard's Sensor page.

Containers:

```bash
cp deploy/.env.example deploy/.env
docker compose -f deploy/docker-compose.yml --env-file deploy/.env up --build
```

## Evidence and custody

Every alert is appended to an append-only SQLite table and linked into a SHA-256 hash chain signed with the sensor's Ed25519 key. An evidence bundle holds the alert, the supporting packets cut from the original capture, SHA-256 values of every file and of the source capture, the public key, and a technical annex listing the hash facts a certificate under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 asks for. `verify-bundle` re-extracts the packets from the original capture and compares them byte for byte. Tests cover an edited alert, a modified capture and a bypassed append-only trigger.

## Limits

* Single-core throughput as measured above.
* Slow beacons are found late (after 8 check-ins).
* Encrypted ClientHello (TLS 1.3 ECH) or QUIC hides SNI; DNS over HTTPS hides DNS entirely.
* Dictionary-word DGAs are largely missed by the character model.
* Validation so far is on synthetic lab traffic; public captures (e.g. CTU-13) and operator traffic are the next step.

See `docs/DESIGN.md` for method details and the sensor's own threat model.
