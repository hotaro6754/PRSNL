"""Case relationship graph and deterministic alert explanation."""

import ipaddress

import pytest

from sentinel.config import Settings
from sentinel.custody import SensorKey
from sentinel.engine import Engine
from sentinel.explain import explain
from sentinel.graphview import build_case_graph
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
    Engine(settings, store).run_capture(str(cap))
    yield store, settings
    store.close()


def test_case_graph_from_real_alerts(analysed):
    store, settings = analysed
    case = store.list_cases(limit=1)[0]
    graph = build_case_graph(store.get_case(case["case_id"]), settings._nets)
    kinds = {n["kind"] for n in graph["nodes"]}
    assert "host" in kinds  # 10.0.9.9 is internal
    assert any(n["kind"] == "threat" and n["label"] == "recon.scan" for n in graph["nodes"])
    # every edge references a real node
    ids = {n["id"] for n in graph["nodes"]}
    assert all(e["source"] in ids and e["target"] in ids for e in graph["edges"])
    assert graph["edges"], "there should be at least one relationship edge"


def test_graph_marks_internal_vs_external():
    nets = [ipaddress.ip_network("10.0.0.0/8")]
    case = {
        "case_id": "C1", "entity": "10.0.5.5",
        "alerts": [{
            "threat_class": "tls.suspicious_session", "severity": "high", "src": "10.0.5.5", "dst": "185.9.9.9",
            "dport": 443, "evidence": [
                {"feature": "tls_ja4", "value": "t13d1516h2_abc_def"},
                {"feature": "tls_sni", "value": "bad-c2.example"},
            ],
        }],
    }
    g = build_case_graph(case, nets)
    kinds = {n["id"]: n["kind"] for n in g["nodes"]}
    assert kinds["10.0.5.5"] == "host" and kinds["185.9.9.9"] == "external"
    assert kinds["bad-c2.example"] == "domain"
    assert any(n["kind"] == "fingerprint" for n in g["nodes"])
    assert any(e["kind"] == "fingerprint" for e in g["edges"])


def test_explain_is_deterministic_and_grounded(analysed):
    store, _ = analysed
    alert = store.list_alerts(limit=1)[0]
    a = explain(alert)
    assert a["summary"].startswith("Sentinel classified traffic")
    assert "recon.scan" in a["summary"] or "scan" in a["summary"].lower()
    assert "T1046" in a["summary"]  # MITRE technique for scanning
    assert "It fired because" in a["why"]
    assert alert["custody"]["hash"][:12] in a["custody"]
    # deterministic: same input, identical output
    assert explain(alert) == a


def test_explain_surfaces_visibility_caveat():
    alert = {
        "threat_class": "exfil.volume", "category": "f", "attack_technique": "T1048", "title": "Asymmetric outbound data volume",
        "severity": "low", "confidence": 0.35, "src": "10.0.6.7", "dst": "91.2.3.4",
        "evidence": [{"feature": "outbound_bytes", "value": 100000000, "threshold": 20000000, "unit": "bytes"}],
        "visibility": {"directions_seen": 1.0, "sufficient": False,
                       "note": "only one direction of this traffic was visible; ratio-based evidence is incomplete"},
        "custody": {"seq": 3, "hash": "abcd1234ef567890"}, "advisory": ["Check what the host holds."],
    }
    a = explain(alert)
    assert "one direction" in a["caveat"]
    assert a["next_steps"] == ["Check what the host holds."]
