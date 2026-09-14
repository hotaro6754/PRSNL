"""Tamper-evident custody for alerts.

Each alert is appended to a hash chain::

    hash_n = SHA-256( f"{n}:{hash_(n-1)}:" || canonical_json(alert without chain fields) )

and ``hash_n`` is signed with the sensor's Ed25519 key. Changing any stored
alert, reordering, or deleting a record breaks every later hash; a forged
record cannot carry a valid signature without the sensor key.

The SHA-256 values and algorithm names recorded here are the technical facts a
certificate under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 asks for.
The certificate itself must still be issued by the responsible person.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

GENESIS = "0" * 64
HASH_ALGORITHM = "SHA-256"
SIGNATURE_ALGORITHM = "Ed25519"


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def chain_payload(alert_doc: dict) -> dict:
    doc = json.loads(json.dumps(alert_doc))
    custody = doc.get("custody") or {}
    for key in ("seq", "prev_hash", "hash", "signature"):
        custody.pop(key, None)
    doc["custody"] = custody
    return doc


def chain_hash(seq: int, prev_hash: str, alert_doc: dict) -> str:
    digest = hashlib.sha256(f"{seq}:{prev_hash}:".encode("ascii"))
    digest.update(canonical(chain_payload(alert_doc)))
    return digest.hexdigest()


class SensorKey:
    """Ed25519 signing key kept on the sensor (never leaves the enclave)."""

    def __init__(self, private_key: Ed25519PrivateKey) -> None:
        self._key = private_key
        self.public_key: Ed25519PublicKey = private_key.public_key()

    @classmethod
    def load_or_create(cls, data_dir: str) -> "SensorKey":
        path = Path(data_dir) / "sensor_ed25519.pem"
        if path.exists():
            key = serialization.load_pem_private_key(path.read_bytes(), password=None)
            return cls(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        key = Ed25519PrivateKey.generate()
        pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                serialization.NoEncryption())
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(pem)
        return cls(key)

    def sign(self, message: str) -> str:
        return base64.b64encode(self._key.sign(message.encode("ascii"))).decode("ascii")

    def public_pem(self) -> str:
        return self.public_key.public_bytes(serialization.Encoding.PEM,
                                            serialization.PublicFormat.SubjectPublicKeyInfo).decode("ascii")

    def fingerprint(self) -> str:
        raw = self.public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return hashlib.sha256(raw).hexdigest()


def verify_signature(public_pem: str, message: str, signature_b64: str) -> bool:
    from cryptography.exceptions import InvalidSignature

    key = serialization.load_pem_public_key(public_pem.encode("ascii"))
    try:
        key.verify(base64.b64decode(signature_b64), message.encode("ascii"))
        return True
    except (InvalidSignature, ValueError):
        return False
