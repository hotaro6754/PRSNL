"""Local development server for the API.

Uses ./var for state and ./lab/captures as the capture directory. The analyst
token is left unset (read endpoints open on localhost); the admin token is
generated and written to var/admin_token unless SENTINEL_ADMIN_TOKEN is set.

    python deploy/dev_api.py
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SENTINEL_DATA_DIR", str(ROOT / "var"))
os.environ.setdefault("SENTINEL_CAPTURE_DIR", str(ROOT / "lab" / "captures"))
os.environ.setdefault("SENTINEL_EVALUATION_REPORT", str(ROOT / "results" / "evaluation.json"))
os.environ.setdefault("SENTINEL_BENCHMARK_REPORT", str(ROOT / "results" / "benchmark.json"))
os.environ.setdefault("SENTINEL_INTERNAL_NETS", "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16")
os.environ.setdefault("SENTINEL_ALLOW_DESTINATIONS", "203.0.113.200")

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run("sentinel.api:app", host="127.0.0.1", port=int(os.getenv("SENTINEL_PORT", "8000")))
