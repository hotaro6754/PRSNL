"""Popular-domain list (Tranco) and offline intelligence files.

Everything is loaded from files inside the enclave; nothing is fetched at runtime.
"""

from __future__ import annotations

import csv
import gzip
from pathlib import Path

INTEL_DIR = Path(__file__).resolve().parent


class TopList:
    def __init__(self, ranks: dict[str, int], source: str) -> None:
        self._ranks = ranks
        self.source = source

    def __len__(self) -> int:
        return len(self._ranks)

    def rank(self, registered_domain: str) -> int | None:
        return self._ranks.get(registered_domain)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "TopList":
        path = Path(path) if path else INTEL_DIR / "tranco_top100k.txt.gz"
        if not path.exists():
            return cls({}, "none")
        ranks: dict[str, int] = {}
        source = str(path.name)
        with gzip.open(path, "rt", encoding="utf-8") as f:
            rank = 0
            for line in f:
                if line.startswith("#"):
                    if line.startswith("# Source:"):
                        source = line[len("# Source:"):].strip()
                    continue
                domain = line.strip()
                if domain:
                    rank += 1
                    ranks.setdefault(domain, rank)
        return cls(ranks, source)


def load_ja3_blocklist(path: str | Path | None = None) -> dict[str, str]:
    """abuse.ch SSLBL JA3 CSV -> {ja3_md5: listing reason}."""
    path = Path(path) if path else INTEL_DIR / "sslbl_ja3.csv"
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.reader(line for line in f if not line.startswith("#")):
            if len(row) >= 4 and len(row[0]) == 32:
                out[row[0].lower()] = row[3]
    return out
