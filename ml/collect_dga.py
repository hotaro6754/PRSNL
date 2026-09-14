"""Collect DGA training domains by running published reverse-engineered DGA
implementations (https://github.com/baderj/domain_generation_algorithms).

That repository is GPL-2.0 and is NOT vendored here: clone it yourself and
point this script at the checkout. Only the generated domain names are stored.

    git clone https://github.com/baderj/domain_generation_algorithms dga-src
    python ml/collect_dga.py dga-src ml/data/dga_domains.csv
"""

from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

DOMAIN = re.compile(r"^[a-z0-9][a-z0-9-]{2,62}(\.[a-z0-9-]{2,63})+$")
MAX_PER_FAMILY = 2000


def run(script: Path, args: list[str]) -> list[str]:
    try:
        out = subprocess.run([sys.executable, script.name, *args], cwd=script.parent, capture_output=True, text=True,
                             timeout=60).stdout
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
    return [line.strip().lower() for line in out.splitlines() if DOMAIN.match(line.strip().lower())]


def main(src: str, dest: str) -> None:
    rows = []
    for family_dir in sorted(p for p in Path(src).iterdir() if p.is_dir() and not p.name.startswith(".")):
        scripts = sorted(s for s in family_dir.glob("*.py") if "test" not in s.name)
        domains: list[str] = []
        for script in scripts:
            domains += run(script, [])
            for date in ("2024-01-15", "2025-06-01", "2026-03-10"):
                if len(domains) >= MAX_PER_FAMILY:
                    break
                domains += run(script, ["-d", date])
        unique = list(dict.fromkeys(domains))[:MAX_PER_FAMILY]
        if unique:
            rows += [(family_dir.name, d) for d in unique]
        print(f"{family_dir.name:<26} {len(unique)}")
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["family", "domain"])
        writer.writerows(rows)
    print(f"wrote {len(rows)} domains from {len({r[0] for r in rows})} families to {dest}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
