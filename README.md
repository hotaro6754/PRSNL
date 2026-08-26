# PS26145 — AI-Driven Network Detection & Response (NDR)

> **SIH 2026 Problem Statement 26145** — Real-time Network Threat Detection using Zeek, XGBoost, and Evidence Fusion

An enterprise-grade, fully containerised Security Operations Center (SOC) platform that passively monitors network traffic via **Zeek**, streams observations through **Redpanda (Kafka)**, runs deterministic + ML-based threat detection, correlates alerts into Security Cases, and presents everything through a production-quality **Next.js** dashboard.

---

## Architecture

```
Network Traffic
     │
     ▼
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│   Zeek   │────▶│ Zeek Adapter │────▶│  Redpanda    │
│  Sensor  │     │  (Python)    │     │  (Kafka)     │
└──────────┘     └──────────────┘     └──────┬──────┘
                                             │
                                             ▼
                                    ┌────────────────┐
                                    │   Backend API   │
                                    │   (FastAPI)     │
                                    │                 │
                                    │ • Window Manager│
                                    │ • Deterministic │
                                    │   Detectors     │
                                    │ • XGBoost v5    │
                                    │ • IsolationFor. │
                                    │ • Correlation   │
                                    │   Engine        │
                                    └───────┬────────┘
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                        ┌──────────┐  ┌──────────┐  ┌──────────┐
                        │ MongoDB  │  │ WebSocket│  │ Prometheus│
                        │ (Cases,  │  │ /alerts  │  │ + Grafana │
                        │  Alerts) │  │          │  │           │
                        └──────────┘  └────┬─────┘  └──────────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  Next.js SOC  │
                                    │  Dashboard    │
                                    │  (Port 3000)  │
                                    └──────────────┘
```

---

## Features

| Layer | What It Does |
|-------|-------------|
| **Zeek Sensor** | Passive packet capture and protocol analysis |
| **Zeek Adapter** | Converts Zeek logs to `NetworkObservation` protobuf and publishes to Redpanda |
| **Redpanda** | Kafka-compatible streaming bus (topic: `network-observations`) |
| **Backend API** | FastAPI server — window aggregation, deterministic detectors (PortScan, BruteForce, DGA, Beaconing, etc.), XGBoost + IsolationForest ML, evidence fusion, correlation engine |
| **MongoDB** | Persistent storage for alerts, cases, ML predictions, model registry, audit logs |
| **ML Worker** | Dedicated inference container for heavy model operations |
| **Prometheus + Grafana** | Infrastructure metrics and dashboards |
| **Next.js Dashboard** | Enterprise SOC UI with live threat stream, case management, analytics, ML intelligence hub, system health, attack simulator |

---

## Prerequisites

- **Docker Desktop** (v4.x+) with Docker Compose v2
- **Git**
- At least **8 GB RAM** allocated to Docker
- Ports `3000`, `8000`, `9090`, `9644`, `19092`, `27017` available

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/hotaro6754/PRSNL.git
cd PRSNL
```

### 2. Create Environment File (Optional)

```bash
cp .env.example .env
```

Default values work out of the box. Override if needed:

```env
APP_ENV=LAB
MONGODB_URI=mongodb://mongodb:27017
REDPANDA_BROKERS=redpanda:9092
API_BASE_URL=http://localhost:8000
```

### 3. Build & Start All Services

```bash
docker compose up -d --build
```

This will spin up **10 containers**:

| Container | Port | Purpose |
|-----------|------|---------|
| `sih26145-frontend` | 3000 | Next.js SOC Dashboard |
| `sih26145-backend` | 8000 | FastAPI Detection Engine |
| `sih26145-zeek` | — | Zeek Passive Sensor |
| `sih26145-zeek-adapter` | — | Log → Kafka Bridge |
| `sih26145-redpanda` | 9644, 19092 | Kafka Message Bus |
| `sih26145-mongodb` | 27017 | Persistent Database |
| `sih26145-ml-worker` | — | ML Inference Worker |
| `sih26145-prometheus` | 9090 | Metrics Collection |
| `sih26145-grafana` | 3001 | Metrics Dashboards |
| `sih26145-lab-dns` | — | Internal DNS (CoreDNS) |

### 4. Wait for Health Checks

```bash
# Check all containers are running
docker compose ps

# Verify backend is healthy
curl http://localhost:8000/health
```

### 5. Open the Dashboard

Navigate to **http://localhost:3000** in your browser.

---

## Dashboard Pages

| Route | Description |
|-------|-------------|
| `/` | **SOC Overview** — KPI cards, network flow rate chart, alert velocity chart |
| `/live` | **Live Threat Stream** — Real-time WebSocket feed of raw detections |
| `/cases` | **Security Cases** — Correlated incident table with search and severity filters |
| `/cases/[id]` | **Case Detail** — Deep-dive into a single incident with alert timeline and evidence |
| `/analytics` | **Threat Analytics** — Severity pie chart, threat vector bar chart, top attacker entities |
| `/ml` | **ML Intelligence** — Model registry, production/canary slots, XGBoost & IsolationForest metadata |
| `/health` | **System Health** — MongoDB, Zeek, Redpanda connection status and diagnostics |
| `/logs` | **Logs & Audit** — Real-time `tail -f` of the backend Python log file |
| `/simulator` | **Attack Simulator** — Trigger real PortScan, BruteForce, and DGA attacks against the internal Zeek sensor |

---

## Generating Real Detections

The **Simulator** page (`/simulator`) generates **real** network traffic — not fake UI data. It instructs the backend to open raw TCP sockets against the Zeek container:

```bash
# Or via API:
curl -X POST http://localhost:8000/api/simulate/port_scan
curl -X POST http://localhost:8000/api/simulate/brute_force
curl -X POST http://localhost:8000/api/simulate/dga
```

The traffic flows through the full pipeline: **Zeek → Redpanda → Detectors → ML → Correlation → MongoDB → Dashboard**.

You can also replay PCAP files:

```bash
curl -X POST http://localhost:8000/replay \
  -H "Content-Type: application/json" \
  -d '{"filename": "sample.pcap"}'
```

Place PCAP files in the `pcaps/` directory.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Full system health with component status |
| `GET` | `/health/ml` | ML model resolver status (production & canary) |
| `GET` | `/api/stats` | Live telemetry counters |
| `GET` | `/api/metrics/history` | Time-series metrics (5s intervals, 1hr window) |
| `GET` | `/api/cases` | List all active security cases |
| `GET` | `/api/cases/{id}` | Get case detail with embedded alerts |
| `GET` | `/api/alerts?limit=100` | Paginated historical alerts from MongoDB |
| `GET` | `/api/logs?lines=200` | Tail backend log file |
| `GET` | `/api/models` | List registered ML models |
| `POST` | `/api/models/register` | Register a new model version |
| `POST` | `/api/models/{id}/versions/{v}/promote` | Promote model to a stage |
| `POST` | `/api/simulate/{type}` | Trigger attack simulation |
| `POST` | `/replay` | Replay a PCAP file |
| `WS` | `/alerts` | Real-time alert WebSocket stream |

---

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Enums, env config, paths
│   ├── correlation.py          # Alert → SecurityCase correlation engine
│   ├── mcp_gateway.py          # MCP tool orchestration
│   ├── schemas.py              # NetworkObservation schema
│   ├── contracts/              # Pydantic data contracts
│   │   ├── alert.py            # Alert schema
│   │   ├── case.py             # SecurityCase schema
│   │   ├── evidence.py         # DetectionEvidence schema
│   │   ├── features.py         # Feature vector contracts
│   │   ├── ml_model.py         # Model registry contracts
│   │   ├── observation.py      # Network observation contracts
│   │   └── prediction.py       # ML prediction contracts
│   ├── detectors/              # Deterministic detection engines
│   ├── features/               # Feature extraction (flow, DNS, TLS)
│   ├── ingestion/              # Data ingestion adapters
│   ├── ml/                     # ML model loading & inference
│   ├── models/                 # Serialised model files (.pkl)
│   ├── replay/                 # PCAP replay engine
│   ├── repositories/           # MongoDB repository layer
│   └── streaming/              # Kafka/Redpanda + Zeek adapters
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx            # Overview dashboard
│   │   ├── layout.tsx          # Global shell with sidebar
│   │   ├── globals.css         # Tailwind v4 styles
│   │   ├── live/page.tsx       # Live WebSocket threat stream
│   │   ├── cases/page.tsx      # Security cases table
│   │   ├── cases/[id]/page.tsx # Case detail view
│   │   ├── analytics/page.tsx  # Threat analytics charts
│   │   ├── ml/page.tsx         # ML Intelligence Hub
│   │   ├── health/page.tsx     # System diagnostics
│   │   ├── logs/page.tsx       # Backend log viewer
│   │   └── simulator/page.tsx  # Attack trigger UI
│   ├── Dockerfile
│   └── package.json
├── tests/                      # Pytest test suite
├── docker-compose.yml          # Full stack orchestration
├── docker-compose.prod.yml     # Production overrides
├── Dockerfile.backend          # Backend container
├── Dockerfile.zeek             # Zeek sensor container
├── prometheus.yml              # Prometheus scrape config
└── requirements.txt            # Python dependencies
```

---

## Stopping the Stack

```bash
docker compose down
```

To remove all data volumes:

```bash
docker compose down -v
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Frontend shows blank page | Run `docker compose up -d --build frontend` to rebuild |
| Backend returns 500 | Check `docker logs sih26145-backend --tail 50` |
| MongoDB connection failed | Ensure `sih26145-mongodb` is healthy: `docker compose ps` |
| Redpanda crash-loops | Ensure `--smp 1` is set in compose (required for existing volumes) |
| No alerts appearing | Use the Simulator page or run `curl -X POST http://localhost:8000/api/simulate/port_scan` |
| Port conflict | Stop any local services on ports 3000, 8000, 9090, 27017 |

---

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Uvicorn, Motor (async MongoDB), confluent-kafka
- **ML:** XGBoost, scikit-learn, IsolationForest, ONNX Runtime
- **Frontend:** Next.js 16, React 19, Tailwind CSS v4, Recharts, Lucide Icons
- **Streaming:** Redpanda (Kafka-compatible)
- **Database:** MongoDB 7
- **Monitoring:** Prometheus, Grafana
- **Sensor:** Zeek IDS
- **Container:** Docker Compose

---

## License

This project was developed for **Smart India Hackathon 2026** (Problem Statement 26145).
