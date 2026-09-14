"""DGA classifier inference: logistic regression over hashed character n-grams
of the registrable label (e.g. ``qxvbtkzn`` in ``qxvbtkzn.biz``).

Weights ship as a NumPy ``.npz`` with a JSON manifest (no pickle is ever
loaded). ``ml/train_dga.py`` produces both using ``feature_indices`` below, so
training and inference cannot drift apart.
"""

from __future__ import annotations

import hashlib
import json
import math
import zlib
from functools import lru_cache
from pathlib import Path

import numpy as np

from sentinel.alerts import ModelRef

N_FEATURES = 1 << 18
_MASK = N_FEATURES - 1


def _h(token: str) -> int:
    return zlib.crc32(token.encode("utf-8")) & _MASK


def feature_indices(label: str) -> list[int]:
    text = f"^{label}$"
    out = [_h(f"{n}|{text[i:i + n]}") for n in (1, 2, 3, 4) for i in range(len(text) - n + 1)]
    length = len(label)
    digits = sum(ch.isdigit() for ch in label)
    vowels = sum(ch in "aeiou" for ch in label)
    out.append(_h(f"len|{min(length, 48) // 3}"))
    out.append(_h(f"digits|{(10 * digits) // max(1, length)}"))
    out.append(_h(f"vowels|{(10 * vowels) // max(1, length)}"))
    out.append(_h(f"hyphen|{'-' in label}"))
    return out


class DgaModel:
    def __init__(self, weights: np.ndarray, bias: float, cal_x: np.ndarray, cal_y: np.ndarray,
                 manifest: dict, sha256: str) -> None:
        self.weights = weights
        self.bias = bias
        self.cal_x = cal_x
        self.cal_y = cal_y
        self.manifest = manifest
        self.sha256 = sha256
        self.probability = lru_cache(maxsize=200_000)(self._probability)

    @classmethod
    def load(cls, path: str | Path) -> "DgaModel":
        path = Path(path)
        raw = path.read_bytes()
        with np.load(path, allow_pickle=False) as data:
            weights = data["weights"].astype(np.float32)
            bias = float(data["bias"])
            cal_x = data["cal_x"].astype(np.float64)
            cal_y = data["cal_y"].astype(np.float64)
        manifest_path = path.with_suffix(".json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        if weights.shape != (N_FEATURES,):
            raise ValueError(f"{path}: expected {N_FEATURES} weights, found {weights.shape}")
        return cls(weights, bias, cal_x, cal_y, manifest, hashlib.sha256(raw).hexdigest())

    def raw_score(self, label: str) -> float:
        idx = feature_indices(label)
        z = self.bias + float(self.weights[idx].sum())
        return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, z))))

    def _probability(self, label: str) -> float:
        p = self.raw_score(label)
        if len(self.cal_x) >= 2:
            return float(np.interp(p, self.cal_x, self.cal_y))
        return p

    def ref(self) -> ModelRef:
        return ModelRef(name=self.manifest.get("name", "dga-char-ngram-lr"),
                        version=self.manifest.get("version", "unknown"), sha256=self.sha256,
                        calibration=self.manifest.get("calibration"))
