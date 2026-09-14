"""HTTP API and live alert stream for the dashboard.

Read endpoints need an analyst token; control endpoints (starting captures,
changing case status) need an admin token. Tokens come from the environment
(SENTINEL_ANALYST_TOKEN, SENTINEL_ADMIN_TOKEN). The API only reads captures
from the configured capture directory: it never accepts a client-supplied
filesystem path, and it never opens a connection toward monitored traffic.

    uvicorn sentinel.api:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import asyncio
import hmac
import json
import logging
import os
import re
import secrets
import threading
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

from sentinel import __version__
from sentinel.alerts import CLASS_META, json_schema
from sentinel.config import Settings
from sentinel.custody import SensorKey
from sentinel.engine import Engine
from sentinel.evidence import build_bundle
from sentinel.store import Store

log = logging.getLogger("sentinel.api")

_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}\.(pcap|pcapng|cap)$")
MAX_UPLOAD_BYTES = int(os.getenv("SENTINEL_MAX_UPLOAD_MB", "2048")) * 1024 * 1024


class State:
    def __init__(self) -> None:
        self.settings = Settings.from_env()
        allow = os.getenv("SENTINEL_ALLOW_DESTINATIONS")
        if allow:
            self.settings.exfil.allow_destinations = tuple(x.strip() for x in allow.split(",") if x.strip())
        data = Path(self.settings.data_dir)
        data.mkdir(parents=True, exist_ok=True)
        self.capture_dir = Path(os.getenv("SENTINEL_CAPTURE_DIR", str(data / "captures"))).resolve()
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self.key = SensorKey.load_or_create(str(data))
        self.store = Store(str(data / "sentinel.db"), self.key)
        self.engine = Engine(self.settings, self.store)
        self.analyst_token = os.getenv("SENTINEL_ANALYST_TOKEN") or ""
        self.admin_token = os.getenv("SENTINEL_ADMIN_TOKEN") or ""
        if not self.admin_token:
            self.admin_token = secrets.token_urlsafe(24)
            log.warning("SENTINEL_ADMIN_TOKEN not set; generated one for this run (see data dir file admin_token)")
            token_file = data / "admin_token"
            token_file.write_text(self.admin_token, encoding="utf-8")
            try:
                os.chmod(token_file, 0o600)
            except OSError:
                pass
        self.subscribers: set[asyncio.Queue] = set()
        self.loop: asyncio.AbstractEventLoop | None = None
        self.job_lock = threading.Lock()
        self.job: dict | None = None
        self.store.subscribe(self._publish)

    def _publish(self, kind: str, doc: dict) -> None:
        if self.loop is None:
            return
        message = {"type": kind, "data": doc}
        for queue in list(self.subscribers):
            self.loop.call_soon_threadsafe(_offer, queue, message)


def _offer(queue: asyncio.Queue, message: dict) -> None:
    if queue.full():
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
    queue.put_nowait(message)


state: State | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global state
    state = State()
    state.loop = asyncio.get_running_loop()
    yield
    state.store.close()


app = FastAPI(title="Sentinel-26145", version=__version__, lifespan=lifespan)
_origins = [o.strip() for o in os.getenv("SENTINEL_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_credentials=False,
                   allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


def _token(authorization: str | None, token: str | None) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return token or ""


def analyst(authorization: str | None = Header(default=None), token: str | None = Query(default=None)) -> str:
    supplied = _token(authorization, token)
    s = state
    if s.analyst_token and not (hmac.compare_digest(supplied, s.analyst_token) or hmac.compare_digest(supplied, s.admin_token)):
        raise HTTPException(401, "missing or invalid analyst token")
    return "analyst"


def admin(authorization: str | None = Header(default=None)) -> str:
    supplied = _token(authorization, None)
    if not supplied or not hmac.compare_digest(supplied, state.admin_token):
        raise HTTPException(401, "admin token required")
    return "admin"


# ---------------------------------------------------------------- read API
@app.get("/api/health")
def health():
    s = state
    return {"status": "ok", "version": __version__, "sensor_id": s.settings.sensor_id,
            "time": time.time(), "job": s.job, "engine": s.engine.health(),
            "sensor_key_sha256": s.key.fingerprint(), "auth": {"analyst_token_required": bool(s.analyst_token)}}


@app.get("/api/overview", dependencies=[Depends(analyst)])
def overview(hours: float = Query(24.0, ge=0.1, le=24 * 365)):
    s = state
    last = s.store.list_alerts(limit=1)
    anchor = last[0]["event_time"] if last else time.time()
    since = anchor - hours * 3600
    counts = s.store.alert_counts(since=since)
    categories = {cat: {"title": title, "classes": []} for cls, (cat, _, title) in CLASS_META.items()}
    for cls, (cat, technique, title) in CLASS_META.items():
        categories[cat]["classes"].append({"threat_class": cls.value, "title": title, "technique": technique,
                                           "count": counts["by_class"].get(cls.value, 0)})
    sources = s.store.list_sources(limit=5)
    return {"window_hours": hours, "window_anchor": anchor, "counts": counts, "categories": categories,
            "open_cases": len(s.store.list_cases(limit=1000, status="open")),
            "recent_sources": sources, "chain_head": s.store.list_alerts(limit=1)[0]["custody"] if last else None}


@app.get("/api/alerts", dependencies=[Depends(analyst)])
def list_alerts(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0),
                threat_class: str | None = None, severity: str | None = None, entity: str | None = None,
                source_id: str | None = None):
    return state.store.list_alerts(limit=limit, offset=offset, threat_class=threat_class, severity=severity,
                                   entity=entity, source_id=source_id)


@app.get("/api/alerts/export", dependencies=[Depends(analyst)])
def export_alerts_endpoint(fmt: str = Query("stix", pattern="^(stix|cef|jsonl)$"),
                           limit: int = Query(1000, ge=1, le=10000), threat_class: str | None = None,
                           severity: str | None = None, since: float | None = None):
    from sentinel.export import export_alerts

    alerts = state.store.list_alerts(limit=limit, threat_class=threat_class, severity=severity, since=since)
    body, content_type = export_alerts(alerts, fmt, state.settings.sensor_id)
    ext = {"stix": "json", "cef": "cef", "jsonl": "jsonl"}[fmt]
    return Response(body, media_type=content_type,
                    headers={"Content-Disposition": f'attachment; filename="sentinel-alerts.{ext}"'})


@app.get("/api/alerts/{alert_id}", dependencies=[Depends(analyst)])
def get_alert(alert_id: str):
    alert = state.store.get_alert(alert_id)
    if alert is None:
        raise HTTPException(404, "alert not found")
    return alert


@app.get("/api/alerts/{alert_id}/bundle", dependencies=[Depends(analyst)])
def alert_bundle(alert_id: str):
    try:
        data = build_bundle(state.store, alert_id)
    except KeyError:
        raise HTTPException(404, "alert not found")
    return Response(data, media_type="application/zip",
                    headers={"Content-Disposition": f'attachment; filename="sentinel-evidence-{alert_id[:12]}.zip"'})


@app.get("/api/hunt", dependencies=[Depends(analyst)])
def hunt_endpoint(indicator: str = Query(..., min_length=2, max_length=256),
                  limit: int = Query(500, ge=1, le=5000)):
    from sentinel.archive import hunt

    result = hunt(state.settings.data_dir, indicator, limit=limit)
    return result


@app.get("/api/audit", dependencies=[Depends(admin)])
def audit_log(limit: int = Query(200, ge=1, le=2000)):
    return state.store.list_audit(limit=limit)


@app.get("/api/cases", dependencies=[Depends(analyst)])
def list_cases(status: str | None = None, limit: int = Query(100, ge=1, le=1000)):
    return state.store.list_cases(limit=limit, status=status)


@app.get("/api/cases/{case_id}", dependencies=[Depends(analyst)])
def get_case(case_id: str):
    case = state.store.get_case(case_id)
    if case is None:
        raise HTTPException(404, "case not found")
    return case


@app.get("/api/cases/{case_id}/graph", dependencies=[Depends(analyst)])
def case_graph(case_id: str):
    from sentinel.graphview import build_case_graph

    case = state.store.get_case(case_id)
    if case is None:
        raise HTTPException(404, "case not found")
    return build_case_graph(case, state.settings._nets)


@app.get("/api/alerts/{alert_id}/explain", dependencies=[Depends(analyst)])
def explain_alert(alert_id: str):
    from sentinel.explain import explain

    alert = state.store.get_alert(alert_id)
    if alert is None:
        raise HTTPException(404, "alert not found")
    return explain(alert)


class CaseStatus(BaseModel):
    status: str
    note: str | None = None
    actor: str = "analyst"


@app.post("/api/cases/{case_id}/status", dependencies=[Depends(admin)])
def set_case_status(case_id: str, body: CaseStatus):
    try:
        case = state.store.set_case_status(case_id, body.status, body.actor[:64], (body.note or "")[:2000] or None)
    except ValueError as exc:
        state.store.audit(body.actor[:64], "case.status", case_id, "rejected", str(exc))
        raise HTTPException(400, str(exc))
    if case is None:
        state.store.audit(body.actor[:64], "case.status", case_id, "not_found")
        raise HTTPException(404, "case not found")
    state.store.audit(body.actor[:64], "case.status", case_id, "ok", f"status={body.status}")
    return case


@app.get("/api/custody/verify", dependencies=[Depends(analyst)])
def verify_custody():
    return state.store.verify_chain()


@app.get("/api/sensor/public-key")
def sensor_public_key():
    return {"public_key_pem": state.key.public_pem(), "sha256": state.key.fingerprint(),
            "algorithm": "Ed25519"}


@app.get("/api/schema/alert")
def alert_schema():
    return json_schema()


@app.get("/api/sources", dependencies=[Depends(analyst)])
def list_sources():
    return state.store.list_sources(limit=100)


@app.get("/api/evaluation", dependencies=[Depends(analyst)])
def evaluation():
    path = Path(os.getenv("SENTINEL_EVALUATION_REPORT", "results/evaluation.json"))
    if not path.exists():
        raise HTTPException(404, "no evaluation report has been generated (run ml/evaluate.py)")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))


@app.get("/api/benchmark", dependencies=[Depends(analyst)])
def benchmark():
    path = Path(os.getenv("SENTINEL_BENCHMARK_REPORT", "results/benchmark.json"))
    if not path.exists():
        raise HTTPException(404, "no benchmark report has been generated (run ml/benchmark.py)")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))


@app.get("/api/flow-export", dependencies=[Depends(analyst)])
def flow_export_report():
    path = Path(os.getenv("SENTINEL_FLOW_EXPORT_REPORT", "results/flow-export-eval.json"))
    if not path.exists():
        raise HTTPException(404, "no flow-export evaluation report (run ml/flow_export_eval.py)")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))


@app.get("/api/models/dga", dependencies=[Depends(analyst)])
def dga_model():
    model = state.engine.dga_model
    if model is None:
        raise HTTPException(404, "DGA model not loaded")
    return {"ref": model.ref().model_dump(), "manifest": model.manifest}


# --------------------------------------------------------------- live stream
@app.get("/api/stream", dependencies=[Depends(analyst)])
async def stream(request: Request):
    queue: asyncio.Queue = asyncio.Queue(maxsize=500)
    state.subscribers.add(queue)

    async def events():
        try:
            yield "retry: 3000\n\n"
            while not await request.is_disconnected():
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield f"event: heartbeat\ndata: {json.dumps({'time': time.time(), 'job': state.job})}\n\n"
                    continue
                yield f"event: {message['type']}\ndata: {json.dumps(message['data'], default=str)}\n\n"
        finally:
            state.subscribers.discard(queue)

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"X-Accel-Buffering": "no", "Cache-Control": "no-store"})


# -------------------------------------------------------------- capture jobs
_FLOW_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}\.(nfv5|nf|netflow|ipfix|flows)$")


@app.get("/api/captures", dependencies=[Depends(analyst)])
def list_captures():
    out = []
    for path in sorted(state.capture_dir.iterdir()):
        if not path.is_file():
            continue
        if _SAFE_NAME.match(path.name):
            out.append({"name": path.name, "size_bytes": path.stat().st_size,
                        "labelled": path.with_suffix(".truth.json").exists(), "kind": "packet"})
        elif _FLOW_NAME.match(path.name):
            out.append({"name": path.name, "size_bytes": path.stat().st_size, "labelled": False, "kind": "flow-export"})
    return out


class ReplayRequest(BaseModel):
    name: str
    speed: float | None = None  # None = as fast as possible, 1.0 = original pacing


def _resolve_capture(name: str) -> Path:
    if not _SAFE_NAME.match(name):
        raise HTTPException(400, "invalid capture name")
    path = (state.capture_dir / name).resolve()
    if path.parent != state.capture_dir or not path.is_file():
        raise HTTPException(404, "capture not found in capture directory")
    return path


def _start_job(path: Path, speed: float | None, label: str, mode: str = "packet") -> dict:
    s = state
    if not s.job_lock.acquire(blocking=False):
        raise HTTPException(409, "a capture is already being processed")
    source_id = uuid.uuid4().hex[:16]
    s.job = {"source_id": source_id, "capture": path.name, "started_at": time.time(), "status": "running",
             "speed": speed, "mode": mode, "progress": None}
    s.store.audit("admin", f"ingest.{mode}", path.name, "started", f"source={source_id}")

    def progress(summary: dict) -> None:
        s.job["progress"] = {k: summary.get(k) for k in ("packets", "flows", "alerts", "packets_per_s", "elapsed_s")}
        s._publish("progress", {"source_id": source_id, **s.job["progress"]})

    def run() -> None:
        try:
            if mode == "flow-export":
                summary = s.engine.run_flow_export(str(path), label=label, source_id=source_id, progress=progress)
            else:
                summary = s.engine.run_capture(str(path), label=label, source_id=source_id, realtime=speed,
                                               progress=progress)
            s.job.update(status=summary["status"], finished_at=time.time(),
                         progress={k: summary.get(k) for k in ("packets", "flows", "alerts", "packets_per_s", "elapsed_s")})
            s.store.audit("admin", f"ingest.{mode}", path.name, summary["status"],
                          f"alerts={summary.get('alerts')} flows={summary.get('flows')}")
            s._publish("source_finished", {"source_id": source_id, "status": summary["status"]})
        except Exception as exc:  # engine logs details; surface a short reason
            s.job.update(status="failed", error=f"{type(exc).__name__}: {exc}")
            s.store.audit("admin", f"ingest.{mode}", path.name, "failed", str(exc))
        finally:
            s.job_lock.release()

    threading.Thread(target=run, name=f"capture-{source_id}", daemon=True).start()
    return s.job


@app.post("/api/captures/replay", dependencies=[Depends(admin)])
def replay(body: ReplayRequest):
    if body.speed is not None and not 0.1 <= body.speed <= 1000:
        raise HTTPException(400, "speed must be between 0.1 and 1000, or null")
    path = _resolve_capture(body.name)
    return _start_job(path, body.speed, f"replay:{path.name}")


@app.post("/api/captures/upload", dependencies=[Depends(admin)])
async def upload(file: UploadFile = File(...)):
    stem = re.sub(r"[^A-Za-z0-9._-]", "_", Path(file.filename or "capture.pcap").name)[:100]
    if not _SAFE_NAME.match(stem):
        raise HTTPException(400, "file must be a .pcap, .pcapng or .cap capture")
    dest = state.capture_dir / f"{int(time.time())}-{stem}"
    size = 0
    with open(dest, "wb") as out:
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "capture exceeds upload limit")
            out.write(chunk)
    with open(dest, "rb") as f:
        magic = f.read(4)
    if magic not in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d", b"\x0a\x0d\x0d\x0a"):
        dest.unlink(missing_ok=True)
        raise HTTPException(400, "file is not a pcap or pcapng capture")
    return _start_job(dest, None, f"upload:{stem}")


class FlowExportRequest(BaseModel):
    name: str


@app.post("/api/flows/analyze", dependencies=[Depends(admin)])
def analyze_flow_export(body: FlowExportRequest):
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}\.(nfv5|nf|netflow|ipfix|flows)$", body.name):
        raise HTTPException(400, "invalid flow-export file name")
    path = (state.capture_dir / body.name).resolve()
    if path.parent != state.capture_dir or not path.is_file():
        raise HTTPException(404, "flow-export file not found in capture directory")
    return _start_job(path, None, f"flow-export:{path.name}", mode="flow-export")
