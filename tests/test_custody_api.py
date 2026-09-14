"""Custody chain tamper detection, evidence bundles, and API access control."""

import json
import sqlite3
import zipfile
import io

import pytest

from sentinel.config import Settings
from sentinel.custody import SensorKey
from sentinel.engine import Engine
from sentinel.evidence import build_bundle, verify_bundle
from sentinel.ingest.pcapio import PcapWriter
from sentinel.lab import packets as P
from sentinel.store import Store


def _scan_capture(path):
    with open(path, "wb") as f:
        w = PcapWriter(f)
        for i, port in enumerate(range(1, 150)):
            t = 1000 + i * 0.01
            w.write(t, P.tcp_packet("10.0.9.9", "10.0.0.10", 40000 + i, port, 1, 0, P.SYN))
            w.write(t + 0.001, P.tcp_packet("10.0.0.10", "10.0.9.9", port, 40000 + i, 0, 2, P.RST | P.ACK))
        w.write(1100, P.udp_packet("10.0.0.1", "10.0.0.2", 1, 2, b"end"))


@pytest.fixture()
def analysed(tmp_path):
    capture = tmp_path / "scan.pcap"
    _scan_capture(capture)
    key = SensorKey.load_or_create(str(tmp_path))
    store = Store(str(tmp_path / "s.db"), key)
    engine = Engine(Settings(internal_nets=("10.0.0.0/8",), data_dir=str(tmp_path)), store)
    summary = engine.run_capture(str(capture))
    yield store, capture, summary, tmp_path
    store.close()


def test_chain_verifies_and_detects_tampering(analysed):
    store, _, summary, tmp_path = analysed
    assert summary["alerts"] >= 1
    assert store.verify_chain()["ok"]
    raw = sqlite3.connect(tmp_path / "s.db")
    with pytest.raises(sqlite3.DatabaseError):
        raw.execute("UPDATE alerts SET severity='low'")
    raw.execute("DROP TRIGGER alerts_append_only_u")  # an attacker with file access bypasses the trigger
    doc = json.loads(raw.execute("SELECT doc FROM alerts WHERE seq=1").fetchone()[0])
    doc["confidence"] = 0.01
    raw.execute("UPDATE alerts SET doc=? WHERE seq=1", (json.dumps(doc),))
    raw.commit()
    result = store.verify_chain()
    assert not result["ok"] and result["failed_seq"] == 1 and "hash" in result["reason"]


def test_bundle_verifies_offline_and_detects_modified_capture(analysed):
    store, capture, _, tmp_path = analysed
    alert = store.list_alerts(limit=1)[0]
    bundle = build_bundle(store, alert["alert_id"])
    zf = zipfile.ZipFile(io.BytesIO(bundle))
    assert {"alert.json", "evidence.pcap", "manifest.json", "sensor_public_key.pem"} <= set(zf.namelist())
    manifest = json.loads(zf.read("manifest.json"))
    assert manifest["evidence_packets"] > 100
    ok = verify_bundle(bundle, str(capture), store.key.fingerprint())
    assert ok["ok"], ok

    tampered = bytearray(capture.read_bytes())
    tampered[-1] ^= 0xFF
    modified = tmp_path / "modified.pcap"
    modified.write_bytes(bytes(tampered))
    bad = verify_bundle(bundle, str(modified))
    assert not bad["ok"]
    assert not next(c for c in bad["checks"] if c["check"] == "source capture hash matches")["ok"]

    alert_doc = json.loads(zf.read("alert.json"))
    alert_doc["severity"] = "low"
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z2:
        for name in zf.namelist():
            z2.writestr(name, json.dumps(alert_doc) if name == "alert.json" else zf.read(name))
    assert not verify_bundle(out.getvalue())["ok"]


def test_api_auth_and_capture_path_safety(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    capture_dir = tmp_path / "captures"
    capture_dir.mkdir()
    _scan_capture(capture_dir / "scan.pcap")
    monkeypatch.setenv("SENTINEL_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("SENTINEL_CAPTURE_DIR", str(capture_dir))
    monkeypatch.setenv("SENTINEL_ANALYST_TOKEN", "analyst-secret")
    monkeypatch.setenv("SENTINEL_ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("SENTINEL_INTERNAL_NETS", "10.0.0.0/8")
    import sentinel.api as api

    with TestClient(api.app) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/api/alerts").status_code == 401
        analyst = {"Authorization": "Bearer analyst-secret"}
        admin = {"Authorization": "Bearer admin-secret"}
        assert client.get("/api/alerts", headers=analyst).json() == []
        assert client.post("/api/captures/replay", json={"name": "scan.pcap"}, headers=analyst).status_code == 401
        assert client.post("/api/captures/replay", json={"name": "../../etc/passwd"}, headers=admin).status_code == 400
        assert client.post("/api/captures/replay", json={"name": "missing.pcap"}, headers=admin).status_code == 404
        started = client.post("/api/captures/replay", json={"name": "scan.pcap"}, headers=admin)
        assert started.status_code == 200
        for _ in range(100):
            job = client.get("/api/health").json()["job"]
            if job["status"] != "running":
                break
            import time
            time.sleep(0.05)
        assert job["status"] == "completed"
        alerts = client.get("/api/alerts", headers=analyst).json()
        assert alerts and alerts[0]["threat_class"] == "recon.scan"
        bundle = client.get(f"/api/alerts/{alerts[0]['alert_id']}/bundle", headers=analyst)
        assert bundle.status_code == 200 and bundle.headers["content-type"] == "application/zip"
        assert client.get("/api/custody/verify", headers=analyst).json()["ok"]
        case_id = client.get("/api/cases", headers=analyst).json()[0]["case_id"]
        upd = client.post(f"/api/cases/{case_id}/status", json={"status": "closed", "note": "confirmed"}, headers=admin)
        assert upd.status_code == 200 and upd.json()["status"] == "closed"
        bad = client.post("/api/captures/upload", files={"file": ("x.pcap", b"not a pcap")}, headers=admin)
        assert bad.status_code == 400
