"""SQLite persistence: append-only alerts on a signed hash chain, cases with an
append-only action log, capture sources and metric snapshots.

Row-level UPDATE/DELETE on alerts and case actions is refused by triggers.
Retention is done by rotating whole database files, never by editing rows.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Callable

from sentinel.alerts import Alert
from sentinel.custody import GENESIS, SensorKey, chain_hash, verify_signature

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    source_id   TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,
    label       TEXT,
    path        TEXT,
    sha256      TEXT,
    started_at  REAL NOT NULL,
    finished_at REAL,
    packets     INTEGER DEFAULT 0,
    bytes       INTEGER DEFAULT 0,
    status      TEXT NOT NULL,
    error       TEXT,
    stats       TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    seq          INTEGER PRIMARY KEY,
    alert_id     TEXT UNIQUE NOT NULL,
    emitted_at   TEXT NOT NULL,
    event_time   REAL NOT NULL,
    threat_class TEXT NOT NULL,
    category     TEXT NOT NULL,
    severity     TEXT NOT NULL,
    confidence   REAL NOT NULL,
    src          TEXT NOT NULL,
    dst          TEXT NOT NULL,
    source_id    TEXT,
    doc          TEXT NOT NULL,
    prev_hash    TEXT NOT NULL,
    hash         TEXT NOT NULL,
    signature    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS alerts_time ON alerts(event_time);
CREATE INDEX IF NOT EXISTS alerts_class ON alerts(threat_class, severity);
CREATE INDEX IF NOT EXISTS alerts_src ON alerts(src);
CREATE INDEX IF NOT EXISTS alerts_dst ON alerts(dst);
CREATE TRIGGER IF NOT EXISTS alerts_append_only_u BEFORE UPDATE ON alerts
BEGIN SELECT RAISE(ABORT, 'alerts are append-only'); END;
CREATE TRIGGER IF NOT EXISTS alerts_append_only_d BEFORE DELETE ON alerts
BEGIN SELECT RAISE(ABORT, 'alerts are append-only'); END;

CREATE TABLE IF NOT EXISTS cases (
    case_id     TEXT PRIMARY KEY,
    entity      TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open',
    severity    TEXT NOT NULL,
    title       TEXT NOT NULL,
    first_seen  REAL NOT NULL,
    last_seen   REAL NOT NULL,
    classes     TEXT NOT NULL,
    alert_count INTEGER NOT NULL DEFAULT 0,
    created_at  REAL NOT NULL,
    updated_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS cases_entity ON cases(entity, status);
CREATE TABLE IF NOT EXISTS case_alerts (
    case_id  TEXT NOT NULL,
    alert_id TEXT NOT NULL,
    PRIMARY KEY (case_id, alert_id)
);
CREATE TABLE IF NOT EXISTS case_actions (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    actor   TEXT NOT NULL,
    action  TEXT NOT NULL,
    note    TEXT,
    at      REAL NOT NULL
);
CREATE TRIGGER IF NOT EXISTS case_actions_append_only_u BEFORE UPDATE ON case_actions
BEGIN SELECT RAISE(ABORT, 'case actions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS case_actions_append_only_d BEFORE DELETE ON case_actions
BEGIN SELECT RAISE(ABORT, 'case actions are append-only'); END;

CREATE TABLE IF NOT EXISTS metrics (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS audit (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    at      REAL NOT NULL,
    actor   TEXT NOT NULL,
    action  TEXT NOT NULL,
    target  TEXT,
    outcome TEXT NOT NULL,
    detail  TEXT
);
CREATE INDEX IF NOT EXISTS audit_at ON audit(at);
CREATE TRIGGER IF NOT EXISTS audit_append_only_u BEFORE UPDATE ON audit
BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_append_only_d BEFORE DELETE ON audit
BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
"""


class Store:
    def __init__(self, path: str, key: SensorKey) -> None:
        self.path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=NORMAL")
        self._db.executescript(_SCHEMA)
        self._lock = threading.RLock()
        self.key = key
        self._listeners: list[Callable[[str, dict], None]] = []

    def close(self) -> None:
        self._db.close()

    def subscribe(self, listener: Callable[[str, dict], None]) -> None:
        self._listeners.append(listener)

    def _notify(self, kind: str, doc: dict) -> None:
        for listener in list(self._listeners):
            try:
                listener(kind, doc)
            except Exception:  # a broken subscriber must not stop persistence
                pass

    # ---------------------------------------------------------------- sources
    def add_source(self, source_id: str, kind: str, label: str | None, path: str | None) -> None:
        with self._lock:
            self._db.execute(
                "INSERT OR REPLACE INTO sources(source_id, kind, label, path, started_at, status) VALUES (?,?,?,?,?,?)",
                (source_id, kind, label, path, time.time(), "running"),
            )

    def finish_source(self, source_id: str, status: str, sha256: str | None, packets: int, nbytes: int,
                      stats: dict | None = None, error: str | None = None) -> None:
        with self._lock:
            self._db.execute(
                "UPDATE sources SET finished_at=?, status=?, sha256=?, packets=?, bytes=?, stats=?, error=? WHERE source_id=?",
                (time.time(), status, sha256, packets, nbytes, json.dumps(stats or {}), error, source_id),
            )

    def update_source_progress(self, source_id: str, packets: int, nbytes: int, stats: dict) -> None:
        with self._lock:
            self._db.execute("UPDATE sources SET packets=?, bytes=?, stats=? WHERE source_id=?",
                             (packets, nbytes, json.dumps(stats), source_id))

    def get_source(self, source_id: str) -> dict | None:
        row = self._db.execute("SELECT * FROM sources WHERE source_id=?", (source_id,)).fetchone()
        return self._source_row(row) if row else None

    def list_sources(self, limit: int = 50) -> list[dict]:
        rows = self._db.execute("SELECT * FROM sources ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._source_row(r) for r in rows]

    @staticmethod
    def _source_row(row: sqlite3.Row) -> dict:
        out = dict(row)
        out["stats"] = json.loads(out["stats"]) if out.get("stats") else {}
        return out

    # ----------------------------------------------------------------- alerts
    def append_alert(self, alert: Alert) -> dict:
        doc = alert.public_dict()
        if doc.get("custody") is None:
            doc["custody"] = {"source_id": "unknown"}
        with self._lock:
            last = self._db.execute("SELECT seq, hash FROM alerts ORDER BY seq DESC LIMIT 1").fetchone()
            seq = last["seq"] + 1 if last else 1
            prev = last["hash"] if last else GENESIS
            digest = chain_hash(seq, prev, doc)
            signature = self.key.sign(digest)
            doc["custody"].update(seq=seq, prev_hash=prev, hash=digest, signature=signature)
            self._db.execute(
                "INSERT INTO alerts(seq, alert_id, emitted_at, event_time, threat_class, category, severity, confidence,"
                " src, dst, source_id, doc, prev_hash, hash, signature) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (seq, doc["alert_id"], doc["emitted_at"], doc["event_time"], doc["threat_class"], doc["category"],
                 doc["severity"], doc["confidence"], doc["src"], doc["dst"], doc["custody"].get("source_id"),
                 json.dumps(doc, separators=(",", ":")), prev, digest, signature),
            )
        self._notify("alert", doc)
        return doc

    def get_alert(self, alert_id: str) -> dict | None:
        row = self._db.execute("SELECT doc FROM alerts WHERE alert_id=?", (alert_id,)).fetchone()
        return json.loads(row["doc"]) if row else None

    def list_alerts(self, limit: int = 100, offset: int = 0, threat_class: str | None = None,
                    severity: str | None = None, since: float | None = None, entity: str | None = None,
                    source_id: str | None = None) -> list[dict]:
        clauses, params = [], []
        if threat_class:
            clauses.append("threat_class = ?")
            params.append(threat_class)
        if severity:
            clauses.append("severity = ?")
            params.append(severity)
        if since is not None:
            clauses.append("event_time >= ?")
            params.append(since)
        if entity:
            clauses.append("(src = ? OR dst = ?)")
            params += [entity, entity]
        if source_id:
            clauses.append("source_id = ?")
            params.append(source_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._db.execute(
            f"SELECT doc FROM alerts {where} ORDER BY seq DESC LIMIT ? OFFSET ?", (*params, limit, offset)
        ).fetchall()
        return [json.loads(r["doc"]) for r in rows]

    def alert_counts(self, since: float | None = None) -> dict:
        where, params = ("WHERE event_time >= ?", (since,)) if since is not None else ("", ())
        by_class = {r[0]: r[1] for r in self._db.execute(
            f"SELECT threat_class, COUNT(*) FROM alerts {where} GROUP BY threat_class", params)}
        by_severity = {r[0]: r[1] for r in self._db.execute(
            f"SELECT severity, COUNT(*) FROM alerts {where} GROUP BY severity", params)}
        by_category = {r[0]: r[1] for r in self._db.execute(
            f"SELECT category, COUNT(*) FROM alerts {where} GROUP BY category", params)}
        total = sum(by_class.values())
        return {"total": total, "by_class": by_class, "by_severity": by_severity, "by_category": by_category}

    def verify_chain(self) -> dict:
        prev = GENESIS
        expected_seq = 1
        public_pem = self.key.public_pem()
        checked = 0
        for row in self._db.execute("SELECT seq, doc, prev_hash, hash, signature FROM alerts ORDER BY seq"):
            doc = json.loads(row["doc"])
            reason = None
            if row["seq"] != expected_seq:
                reason = f"sequence gap: expected {expected_seq}, found {row['seq']}"
            elif row["prev_hash"] != prev:
                reason = "previous-hash link broken"
            elif chain_hash(row["seq"], row["prev_hash"], doc) != row["hash"]:
                reason = "record content does not match its hash"
            elif not verify_signature(public_pem, row["hash"], row["signature"]):
                reason = "signature does not verify with the sensor key"
            if reason:
                return {"ok": False, "checked": checked, "failed_seq": row["seq"], "reason": reason}
            prev = row["hash"]
            expected_seq += 1
            checked += 1
        return {"ok": True, "checked": checked, "head_seq": expected_seq - 1, "head_hash": prev,
                "hash_algorithm": "SHA-256", "signature_algorithm": "Ed25519",
                "sensor_key_fingerprint": self.key.fingerprint()}

    # ------------------------------------------------------------------ cases
    def open_case_for(self, entity: str) -> dict | None:
        row = self._db.execute(
            "SELECT * FROM cases WHERE entity=? AND status IN ('open','investigating') ORDER BY last_seen DESC LIMIT 1",
            (entity,),
        ).fetchone()
        return self._case_row(row) if row else None

    def upsert_case(self, case: dict, alert_id: str) -> dict:
        now = time.time()
        with self._lock:
            self._db.execute(
                "INSERT INTO cases(case_id, entity, status, severity, title, first_seen, last_seen, classes, alert_count,"
                " created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(case_id) DO UPDATE SET"
                " severity=excluded.severity, title=excluded.title, last_seen=excluded.last_seen,"
                " classes=excluded.classes, alert_count=excluded.alert_count, updated_at=excluded.updated_at",
                (case["case_id"], case["entity"], case.get("status", "open"), case["severity"], case["title"],
                 case["first_seen"], case["last_seen"], json.dumps(case["classes"]), case["alert_count"], now, now),
            )
            self._db.execute("INSERT OR IGNORE INTO case_alerts(case_id, alert_id) VALUES (?,?)",
                             (case["case_id"], alert_id))
        doc = self.get_case(case["case_id"], with_alerts=False)
        self._notify("case", doc)
        return doc

    def set_case_status(self, case_id: str, status: str, actor: str, note: str | None) -> dict | None:
        if status not in ("open", "investigating", "closed", "false_positive"):
            raise ValueError(f"unknown status {status!r}")
        with self._lock:
            cur = self._db.execute("UPDATE cases SET status=?, updated_at=? WHERE case_id=?",
                                   (status, time.time(), case_id))
            if cur.rowcount == 0:
                return None
            self._db.execute("INSERT INTO case_actions(case_id, actor, action, note, at) VALUES (?,?,?,?,?)",
                             (case_id, actor, f"status:{status}", note, time.time()))
        return self.get_case(case_id)

    def get_case(self, case_id: str, with_alerts: bool = True) -> dict | None:
        row = self._db.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
        if not row:
            return None
        case = self._case_row(row)
        if with_alerts:
            rows = self._db.execute(
                "SELECT a.doc FROM case_alerts c JOIN alerts a ON a.alert_id = c.alert_id WHERE c.case_id=? ORDER BY a.seq",
                (case_id,),
            ).fetchall()
            case["alerts"] = [json.loads(r["doc"]) for r in rows]
            case["actions"] = [dict(r) for r in self._db.execute(
                "SELECT actor, action, note, at FROM case_actions WHERE case_id=? ORDER BY id", (case_id,))]
        return case

    def list_cases(self, limit: int = 100, status: str | None = None) -> list[dict]:
        if status:
            rows = self._db.execute("SELECT * FROM cases WHERE status=? ORDER BY last_seen DESC LIMIT ?",
                                    (status, limit)).fetchall()
        else:
            rows = self._db.execute("SELECT * FROM cases ORDER BY last_seen DESC LIMIT ?", (limit,)).fetchall()
        return [self._case_row(r) for r in rows]

    @staticmethod
    def _case_row(row: sqlite3.Row) -> dict:
        out = dict(row)
        out["classes"] = json.loads(out["classes"])
        return out

    # ---------------------------------------------------------------- metrics
    def put_metric(self, key: str, value: Any) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO metrics(key, value, updated_at) VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET"
                " value=excluded.value, updated_at=excluded.updated_at",
                (key, json.dumps(value), time.time()),
            )

    def get_metric(self, key: str) -> Any:
        row = self._db.execute("SELECT value, updated_at FROM metrics WHERE key=?", (key,)).fetchone()
        return {"value": json.loads(row["value"]), "updated_at": row["updated_at"]} if row else None

    # ------------------------------------------------------------------ audit
    def audit(self, actor: str, action: str, target: str | None, outcome: str, detail: str | None = None) -> None:
        with self._lock:
            self._db.execute("INSERT INTO audit(at, actor, action, target, outcome, detail) VALUES (?,?,?,?,?,?)",
                             (time.time(), actor, action, target, outcome, detail))

    def list_audit(self, limit: int = 200) -> list[dict]:
        rows = self._db.execute("SELECT at, actor, action, target, outcome, detail FROM audit ORDER BY id DESC LIMIT ?",
                                (limit,)).fetchall()
        return [dict(r) for r in rows]
