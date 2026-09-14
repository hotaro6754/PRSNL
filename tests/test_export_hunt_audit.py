"""STIX/CEF export, flow-archive retro-hunt, and the audit log."""

import json

import pytest

from sentinel.archive import hunt
from sentinel.config import Settings
from sentinel.custody import SensorKey
from sentinel.engine import Engine
from sentinel.export import alerts_to_stix_bundle, alert_to_cef, export_alerts
from sentinel.ingest.pcapio import PcapWriter
from sentinel.lab import packets as P
from sentinel.store import Store


def _scan_capture(path):
    with open(path, "wb") as f:
        w = PcapWriter(f)
        for i, port in enumerate(range(1, 160)):
            t = 1000 + i * 0.01
            w.write(t, P.tcp_packet("10.0.9.9", "10.0.0.10", 40000 + i, port, 1, 0, P.SYN))
            w.write(t + 0.001, P.tcp_packet("10.0.0.10", "10.0.9.9", port, 40000 + i, 0, 2, P.RST | P.ACK))
        w.write(1100, P.udp_packet("10.0.0.1", "10.0.0.2", 1, 2, b"end"))


@pytest.fixture()
def analysed(tmp_path):
    cap = tmp_path / "scan.pcap"
    _scan_capture(cap)
    store = Store(str(tmp_path / "s.db"), SensorKey.load_or_create(str(tmp_path)))
    settings = Settings(internal_nets=("10.0.0.0/8",), data_dir=str(tmp_path))
    engine = Engine(settings, store)
    engine.run_capture(str(cap))
    yield store, settings, tmp_path
    store.close()


def test_stix_bundle_is_valid_and_carries_custody_hash(analysed):
    store, settings, _ = analysed
    alerts = store.list_alerts(limit=50)
    assert alerts
    bundle = alerts_to_stix_bundle(alerts, settings.sensor_id)
    assert bundle["type"] == "bundle" and bundle["id"].startswith("bundle--")
    types = {o["type"] for o in bundle["objects"]}
    assert {"indicator", "sighting", "identity"} <= types
    indicator = next(o for o in bundle["objects"] if o["type"] == "indicator")
    assert indicator["pattern"].startswith("[") and indicator["spec_version"] == "2.1"
    assert any(r["source_name"] == "mitre-attack" for r in indicator["external_references"])
    custody_ref = next(r for r in indicator["external_references"] if r["source_name"] == "sentinel-26145")
    assert store.list_alerts(limit=1)[0]["custody"]["hash"] in custody_ref["description"]


def test_cef_line_shape(analysed):
    store, settings, _ = analysed
    alert = store.list_alerts(limit=1)[0]
    line = alert_to_cef(alert, settings.sensor_id)
    assert line.startswith("CEF:0|NTRO|Sentinel-26145|1.0|recon.scan|")
    assert "cs1Label=threatClass cs1=recon.scan" in line
    assert f"externalId={alert['alert_id']}" in line
    body, ctype = export_alerts(store.list_alerts(limit=50), "cef", settings.sensor_id)
    assert ctype == "text/plain" and body.count("CEF:0|") == len(store.list_alerts(limit=50))


def test_retro_hunt_finds_archived_flows(analysed):
    store, settings, tmp_path = analysed
    # the scan wrote a flow archive under the data dir; hunt for the scanner IP
    result = hunt(str(tmp_path), "10.0.9.9", limit=1000)
    assert result["sources"] >= 1
    assert result["matches"], "scanner flows should be archived"
    assert all(m["src"] == "10.0.9.9" or m["dst"] == "10.0.9.9" for m in result["matches"])
    assert hunt(str(tmp_path), "203.0.113.250")["matches"] == []


def test_audit_log_append_only(analysed):
    store, _, _ = analysed
    store.audit("admin", "test.action", "target-1", "ok", "detail")
    rows = store.list_audit(limit=10)
    assert rows and rows[0]["action"] == "test.action" and rows[0]["outcome"] == "ok"
    import sqlite3
    with pytest.raises(sqlite3.DatabaseError):
        store._db.execute("UPDATE audit SET outcome='tampered'")
    with pytest.raises(sqlite3.DatabaseError):
        store._db.execute("DELETE FROM audit")


def test_api_export_hunt_audit(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    capture_dir = tmp_path / "captures"
    capture_dir.mkdir()
    _scan_capture(capture_dir / "scan.pcap")
    monkeypatch.setenv("SENTINEL_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("SENTINEL_CAPTURE_DIR", str(capture_dir))
    monkeypatch.setenv("SENTINEL_ANALYST_TOKEN", "a-secret")
    monkeypatch.setenv("SENTINEL_ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("SENTINEL_INTERNAL_NETS", "10.0.0.0/8")
    import sentinel.api as api

    analyst = {"Authorization": "Bearer a-secret"}
    admin = {"Authorization": "Bearer admin-secret"}
    with TestClient(api.app) as client:
        started = client.post("/api/captures/replay", json={"name": "scan.pcap"}, headers=admin)
        assert started.status_code == 200
        import time
        for _ in range(120):
            if client.get("/api/health").json()["job"]["status"] != "running":
                break
            time.sleep(0.05)
        # STIX export
        stix = client.get("/api/alerts/export?fmt=stix", headers=analyst)
        assert stix.status_code == 200
        bundle = json.loads(stix.text)
        assert bundle["type"] == "bundle" and bundle["objects"]
        # CEF export
        cef = client.get("/api/alerts/export?fmt=cef", headers=analyst)
        assert "CEF:0|NTRO|Sentinel-26145" in cef.text
        # retro-hunt
        h = client.get("/api/hunt?indicator=10.0.9.9", headers=analyst).json()
        assert h["matches"] and h["matches"][0]["src"] == "10.0.9.9"
        # audit log is admin-only and records the ingest
        assert client.get("/api/audit", headers=analyst).status_code == 401
        audit = client.get("/api/audit", headers=admin).json()
        assert any(row["action"] == "ingest.packet" for row in audit)
