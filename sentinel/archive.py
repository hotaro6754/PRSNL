"""Append-only flow archive for retro-hunting.

The problem statement's inputs include exported flow records; keeping a bounded
archive of the flows the sensor observed lets an analyst hunt an indicator (an
IP, a domain, a JA4) across history after new intelligence arrives — the same
job RITA/Zeek logs do, but written by our own meter. Records are gzipped JSONL,
one file per source, so the archive streams and never needs to be held in memory.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from sentinel.events import FlowRecord

_FIELDS = ("first_ts", "last_ts", "proto", "src", "sport", "dst", "dport", "orig_pkts", "orig_bytes",
           "resp_pkts", "resp_bytes", "state", "community_id")


class FlowArchiveWriter:
    def __init__(self, root: str, source_id: str, max_flows: int) -> None:
        self.path = Path(root) / "flows" / f"{source_id}.jsonl.gz"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = gzip.open(self.path, "at", encoding="utf-8")
        self.written = 0
        self.max_flows = max_flows

    def write(self, rec: FlowRecord) -> None:
        if self.written >= self.max_flows:
            return
        row = {k: getattr(rec, k) for k in _FIELDS}
        if rec.tls and rec.tls.ja4:
            row["ja4"] = rec.tls.ja4
        if rec.tls and rec.tls.sni:
            row["sni"] = rec.tls.sni
        self._fh.write(json.dumps(row, separators=(",", ":")) + "\n")
        self.written += 1

    def close(self) -> None:
        try:
            self._fh.close()
        except Exception:
            pass


def hunt(root: str, indicator: str, limit: int = 1000) -> dict:
    """Search every archived flow file for an indicator (IP substring, domain, or JA4)."""
    flows_dir = Path(root) / "flows"
    needle = indicator.strip().lower()
    matches: list[dict] = []
    scanned = 0
    files = sorted(flows_dir.glob("*.jsonl.gz")) if flows_dir.exists() else []
    for fp in files:
        source_id = fp.name[:-len(".jsonl.gz")]
        try:
            with gzip.open(fp, "rt", encoding="utf-8") as fh:
                for line in fh:
                    scanned += 1
                    if needle not in line.lower():
                        continue
                    row = json.loads(line)
                    hay = f"{row.get('src','')} {row.get('dst','')} {row.get('sni','')} {row.get('ja4','')}".lower()
                    if needle in hay:
                        row["source_id"] = source_id
                        matches.append(row)
                        if len(matches) >= limit:
                            return {"indicator": indicator, "matches": matches, "flows_scanned": scanned,
                                    "truncated": True, "sources": len(files)}
        except OSError:
            continue
    matches.sort(key=lambda r: r.get("first_ts", 0))
    return {"indicator": indicator, "matches": matches, "flows_scanned": scanned, "truncated": False,
            "sources": len(files)}
