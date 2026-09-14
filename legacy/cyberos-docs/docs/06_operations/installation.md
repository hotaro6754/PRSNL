# Installation & Configuration

## Prerequisites
* Python 3.10+
* Docker Desktop (or Linux Docker daemon)
* Git

## Directory Structure
```text
sih26145-prototype/
├── backend/
│   ├── detectors/
│   ├── ml/
│   └── streaming/
├── frontend/
├── tests/
├── models/
└── deployment/
```

## Running the Stack
```bash
docker-compose up -d redis redpanda mongodb
```
*Expected Output*: Containers spin up cleanly.
*Common Failure*: Port 6379 already in use (stop local Redis).