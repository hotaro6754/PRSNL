"""Evidence bundles: the alert, the packets that support it, and everything
needed to verify both offline.

Bundle layout (zip)::

    alert.json                   the stored alert record (with custody chain fields)
    evidence.pcap                supporting packets cut from the original capture
    manifest.json                SHA-256 of every file, chain hash, signature, source capture hash
    sensor_public_key.pem        Ed25519 key that signed the chain entry
    section63_technical_annex.txt  hash facts in a form usable for a BSA s.63 certificate
    VERIFY.md                    how to check the bundle
"""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from sentinel import __version__
from sentinel.alerts import EvidenceScope
from sentinel.custody import HASH_ALGORITHM, SIGNATURE_ALGORITHM, chain_hash, verify_signature
from sentinel.ingest.flowmeter import FlowMeter
from sentinel.ingest.pcapio import PcapReader, PcapWriter, sha256_file
from sentinel.store import Store


def extract_packets(capture_path: str, scope: EvidenceScope) -> tuple[list, int]:
    """Return ([(ts, data, wire_len)], linktype) for packets inside the scope."""
    hosts = set(scope.hosts)
    ports = set(scope.ports)
    out = []
    reader = PcapReader(capture_path)
    linktype = 1
    try:
        for pkt in reader:
            linktype = pkt.linktype
            if scope.offset_hi >= 0 and pkt.offset > scope.offset_hi:
                break
            if scope.offset_lo >= 0 and 0 <= pkt.offset < scope.offset_lo:
                continue
            if pkt.ts < scope.t0 - 1.0:
                continue
            if pkt.ts > scope.t1 + 60.0:
                break
            if pkt.ts > scope.t1 + 1.0:
                continue
            parsed = FlowMeter._decode(pkt.linktype, pkt.data)
            if parsed is None:
                continue
            proto, src, dst, _ip_len, l4, _l4_len = parsed
            if scope.proto is not None and proto != scope.proto:
                continue
            if hosts and src not in hosts and dst not in hosts:
                continue
            if ports:
                if l4 is None or len(l4) < 4 or proto not in (6, 17):
                    continue
                sport = int.from_bytes(l4[0:2], "big")
                dport = int.from_bytes(l4[2:4], "big")
                if sport not in ports and dport not in ports:
                    continue
            out.append((pkt.ts, pkt.data, pkt.wire_len))
            if len(out) >= scope.max_packets:
                break
    finally:
        reader.close()
    return out, linktype


def build_bundle(store: Store, alert_id: str) -> bytes:
    alert = store.get_alert(alert_id)
    if alert is None:
        raise KeyError(alert_id)
    custody = alert.get("custody") or {}
    source = store.get_source(custody.get("source_id", "")) or {}
    capture_path = source.get("path")
    scope = EvidenceScope(**custody["scope"]) if custody.get("scope") else None

    pcap_bytes = b""
    packet_count = 0
    source_note = None
    if scope and capture_path and capture_path != "-" and Path(capture_path).exists():
        current = sha256_file(capture_path)
        if source.get("sha256") and current != source["sha256"]:
            source_note = "capture file changed since analysis: packets NOT extracted"
        else:
            packets, linktype = extract_packets(capture_path, scope)
            buf = io.BytesIO()
            writer = PcapWriter(buf, linktype)
            for ts, data, wire_len in packets:
                writer.write(ts, data, wire_len)
            pcap_bytes = buf.getvalue()
            packet_count = len(packets)
    else:
        source_note = "source capture not available on this sensor: packets not included"

    alert_json = json.dumps(alert, indent=2, sort_keys=True).encode("utf-8")
    public_pem = store.key.public_pem()
    files = {"alert.json": alert_json, "sensor_public_key.pem": public_pem.encode("ascii")}
    if pcap_bytes:
        files["evidence.pcap"] = pcap_bytes
    manifest = {
        "bundle_format": "sentinel.evidence/1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": f"sentinel {__version__}",
        "alert_id": alert_id,
        "chain": {"seq": custody.get("seq"), "prev_hash": custody.get("prev_hash"), "hash": custody.get("hash"),
                  "signature": custody.get("signature"), "hash_algorithm": HASH_ALGORITHM,
                  "signature_algorithm": SIGNATURE_ALGORITHM},
        "sensor": {"sensor_id": alert.get("sensor_id"), "public_key_sha256": store.key.fingerprint()},
        "source_capture": {"source_id": source.get("source_id"), "file_name": Path(capture_path).name if capture_path else None,
                           "sha256": source.get("sha256"), "packets": source.get("packets"), "note": source_note},
        "evidence_packets": packet_count,
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
    }
    annex = _section63_annex(alert, manifest)
    files["section63_technical_annex.txt"] = annex.encode("utf-8")
    manifest["files"]["section63_technical_annex.txt"] = hashlib.sha256(files["section63_technical_annex.txt"]).hexdigest()
    files["manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
    files["VERIFY.md"] = _VERIFY_TEXT.encode("utf-8")

    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return out.getvalue()


def verify_bundle(bundle: bytes | str | Path, capture_path: str | None = None,
                  expected_key_fingerprint: str | None = None) -> dict:
    data = Path(bundle).read_bytes() if isinstance(bundle, (str, Path)) else bundle
    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = set(zf.namelist())
        manifest = json.loads(zf.read("manifest.json"))
        alert = json.loads(zf.read("alert.json"))
        public_pem = zf.read("sensor_public_key.pem").decode("ascii")
        for name, digest in manifest["files"].items():
            present = name in names
            check(f"file hash: {name}", present and hashlib.sha256(zf.read(name)).hexdigest() == digest,
                  "missing" if not present else "")
        pcap = zf.read("evidence.pcap") if "evidence.pcap" in names else None

    custody = alert.get("custody") or {}
    chain = manifest["chain"]
    recomputed = chain_hash(custody["seq"], custody["prev_hash"], alert)
    check("alert content matches chain hash", recomputed == custody.get("hash") == chain["hash"])
    check("chain hash signed by sensor key", verify_signature(public_pem, chain["hash"], chain["signature"]))
    from cryptography.hazmat.primitives import serialization

    raw = serialization.load_pem_public_key(public_pem.encode("ascii")).public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    fingerprint = hashlib.sha256(raw).hexdigest()
    check("key fingerprint matches manifest", fingerprint == manifest["sensor"]["public_key_sha256"])
    if expected_key_fingerprint:
        check("key fingerprint matches the trusted sensor key", fingerprint == expected_key_fingerprint)
    if capture_path:
        source_hash = sha256_file(capture_path)
        check("source capture hash matches", source_hash == manifest["source_capture"]["sha256"], source_hash)
        if pcap is not None and custody.get("scope"):
            packets, linktype = extract_packets(capture_path, EvidenceScope(**custody["scope"]))
            buf = io.BytesIO()
            writer = PcapWriter(buf, linktype)
            for ts, pdata, wire_len in packets:
                writer.write(ts, pdata, wire_len)
            check("evidence packets re-extracted identically", buf.getvalue() == pcap)
    return {"ok": all(c["ok"] for c in checks), "alert_id": alert.get("alert_id"), "checks": checks}


def _section63_annex(alert: dict, manifest: dict) -> str:
    source = manifest["source_capture"]
    return f"""TECHNICAL ANNEX - ELECTRONIC RECORD HASH FACTS
(for use by the responsible person or expert preparing a certificate under Section 63,
Bharatiya Sakshya Adhiniyam, 2023; this annex is not itself the certificate)

Producing system        : Sentinel-26145 {manifest['generator']} (passive, receive-only monitoring sensor)
Sensor identifier       : {manifest['sensor']['sensor_id']}
Alert identifier        : {alert.get('alert_id')}
Alert event time (UTC)  : {datetime.fromtimestamp(alert.get('event_time', 0), timezone.utc).isoformat()}
Threat class            : {alert.get('threat_class')} ({alert.get('title')})

Source capture file     : {source.get('file_name')}
Source capture {HASH_ALGORITHM}  : {source.get('sha256')}
Evidence extract file   : evidence.pcap ({manifest['evidence_packets']} packets)
Evidence extract {HASH_ALGORITHM}: {manifest['files'].get('evidence.pcap', 'not included')}
Alert record {HASH_ALGORITHM}    : {manifest['files'].get('alert.json')}

Custody chain position  : {manifest['chain']['seq']}
Chain hash ({HASH_ALGORITHM})    : {manifest['chain']['hash']}
Previous chain hash     : {manifest['chain']['prev_hash']}
Signature algorithm     : {SIGNATURE_ALGORITHM}
Signing key {HASH_ALGORITHM}     : {manifest['sensor']['public_key_sha256']}

Hash algorithm for all values above: {HASH_ALGORITHM}
"""


_VERIFY_TEXT = """# Verifying this evidence bundle

1. Every file's SHA-256 must match `manifest.json` -> `files`.
2. Recompute the chain hash: SHA-256 of `"{seq}:{prev_hash}:"` followed by the canonical JSON
   (sorted keys, no whitespace) of `alert.json` with `custody.seq`, `custody.prev_hash`,
   `custody.hash` and `custody.signature` removed. It must equal `manifest.json` -> `chain.hash`.
3. Verify `chain.signature` (Ed25519, base64) over the ASCII chain hash with `sensor_public_key.pem`,
   and compare the key's SHA-256 fingerprint with the fingerprint published for this sensor.
4. With the original capture: its SHA-256 must equal `source_capture.sha256`, and cutting the packets
   described by `alert.json` -> `custody.scope` must reproduce `evidence.pcap` byte for byte.

Automated: `python -m sentinel verify-bundle bundle.zip --capture original.pcap --fingerprint <sensor key sha256>`
"""
