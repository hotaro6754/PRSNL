"""Train, calibrate and evaluate the DGA classifier.

Data
  malicious  ml/data/dga_domains.csv   (family, domain)  from ml/collect_dga.py
  benign     Tranco top-1M list        (rank, domain)

Splits (no random row split - that leaks family structure):
  * DGA families are split by FAMILY: test families are never seen in training,
    so reported recall is recall on unseen malware families.
  * Benign domains are split by RANK: ranks 1..400k train/validation,
    ranks 400k..1M test (unpopular names look most like DGA output; the runtime
    detector additionally skips anything in the top-100k list).

Outputs
  models/dga/dga_char_ngram_lr.npz   weights, bias, isotonic calibration table
  models/dga/dga_char_ngram_lr.json  manifest with data provenance and test metrics
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import tldextract
from scipy.sparse import csr_matrix
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, precision_recall_fscore_support, roc_auc_score

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sentinel.detect.dga_model import N_FEATURES, DgaModel, feature_indices  # noqa: E402

EXTRACT = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)
TEST_FAMILIES_DEFAULT = ["necurs", "qakbot", "simda", "suppobox", "nymaim2", "tinba", "ramdo", "zloader", "padcrypt",
                         "sisron"]


def label_of(domain: str) -> str:
    return EXTRACT(domain).domain.lower()


def matrix(labels: list[str]) -> csr_matrix:
    rows, cols = [], []
    for i, label in enumerate(labels):
        idx = feature_indices(label)
        rows += [i] * len(idx)
        cols += idx
    data = np.ones(len(cols), dtype=np.float32)
    m = csr_matrix((data, (rows, cols)), shape=(len(labels), N_FEATURES), dtype=np.float32)
    m.sum_duplicates()
    return m


def load_benign(path: Path) -> list[tuple[int, str]]:
    if path.suffix == ".zip":
        text = zipfile.ZipFile(path).read("top-1m.csv").decode()
    else:
        text = path.read_text(encoding="utf-8")
    out = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) >= 2:
            label = label_of(row[1])
            if len(label) >= 6:
                out.append((int(row[0]), label))
    return out


def metrics_at(y: np.ndarray, p: np.ndarray, threshold: float) -> dict:
    pred = (p >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    fpr = float(((pred == 1) & (y == 0)).sum() / max(1, (y == 0).sum()))
    return {"threshold": threshold, "precision": round(float(precision), 4), "recall": round(float(recall), 4),
            "f1": round(float(f1), 4), "false_positive_rate": round(fpr, 6)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dga", default="ml/data/dga_domains.csv")
    ap.add_argument("--benign", required=True, help="Tranco top-1m.csv or its zip")
    ap.add_argument("--out", default="models/dga/dga_char_ngram_lr.npz")
    ap.add_argument("--test-families", nargs="*", default=TEST_FAMILIES_DEFAULT)
    ap.add_argument("--seed", type=int, default=26145)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    by_family: dict[str, list[str]] = defaultdict(list)
    with open(args.dga, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label = label_of(row["domain"])
            if len(label) >= 6:
                by_family[row["family"]].append(label)
    test_families = [fam for fam in args.test_families if fam in by_family]
    train_families = [fam for fam in by_family if fam not in test_families]

    benign = load_benign(Path(args.benign))
    benign_train_pool = sorted({label for rank, label in benign if rank <= 400_000})
    benign_test_pool = sorted({label for rank, label in benign if rank > 400_000} - set(benign_train_pool))
    rng.shuffle(benign_train_pool)
    rng.shuffle(benign_test_pool)

    dga_train, dga_val = [], []
    for fam in train_families:
        labels = list(dict.fromkeys(by_family[fam]))
        rng.shuffle(labels)
        cut = max(1, int(0.8 * len(labels)))
        dga_train += labels[:cut]
        dga_val += labels[cut:]
    dga_test = [label for fam in test_families for label in dict.fromkeys(by_family[fam])]
    test_family_of = [fam for fam in test_families for _ in dict.fromkeys(by_family[fam])]

    n_benign_train = min(len(benign_train_pool) - 20_000, 6 * len(dga_train))
    benign_train = benign_train_pool[:n_benign_train]
    benign_val = benign_train_pool[n_benign_train:n_benign_train + 20_000]
    benign_test = benign_test_pool[:100_000]

    x_train = matrix(benign_train + dga_train)
    y_train = np.array([0] * len(benign_train) + [1] * len(dga_train))
    clf = LogisticRegression(C=4.0, max_iter=2000, solver="liblinear", class_weight="balanced")
    clf.fit(x_train, y_train)

    weights = clf.coef_.ravel().astype(np.float32)
    bias = float(clf.intercept_[0])
    tmp = DgaModel(weights, bias, np.array([]), np.array([]), {}, "")

    val_labels = benign_val + dga_val
    y_val = np.array([0] * len(benign_val) + [1] * len(dga_val))
    raw_val = np.array([tmp.raw_score(label) for label in val_labels])
    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(raw_val, y_val)
    grid = np.unique(np.concatenate([np.linspace(0, 1, 201), iso.X_thresholds_]))
    cal_y = iso.predict(grid)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, weights=weights, bias=np.array(bias), cal_x=grid, cal_y=cal_y)
    model = DgaModel.load(out)

    test_labels = benign_test + dga_test
    y_test = np.array([0] * len(benign_test) + [1] * len(dga_test))
    p_test = np.array([model.probability(label) for label in test_labels])
    per_family = {}
    for fam in test_families:
        mask = np.array([False] * len(benign_test) + [f == fam for f in test_family_of])
        per_family[fam] = {"domains": int(mask.sum()), "recall_at_0.9": round(float((p_test[mask] >= 0.9).mean()), 4)}

    manifest = {
        "name": "dga-char-ngram-lr",
        "version": datetime.now(timezone.utc).strftime("%Y.%m.%d"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "calibration": "isotonic (validation split)",
        "features": f"hashed character 1-4 grams of the registrable label + length/digit/vowel/hyphen buckets, {N_FEATURES} dims",
        "classifier": "L2 logistic regression (liblinear, C=4, balanced class weights)",
        "data": {
            "dga_source": "outputs of reverse-engineered DGA implementations, github.com/baderj/domain_generation_algorithms",
            "benign_source": "Tranco top-1M list (https://tranco-list.eu)",
            "train_families": sorted(train_families),
            "test_families_held_out": sorted(test_families),
            "counts": {"train_benign": len(benign_train), "train_dga": len(dga_train), "val_benign": len(benign_val),
                       "val_dga": len(dga_val), "test_benign": len(benign_test), "test_dga": len(dga_test)},
            "benign_split": "train/val ranks 1-400k, test ranks 400k-1M",
        },
        "test_metrics": {
            "roc_auc": round(float(roc_auc_score(y_test, p_test)), 4),
            "average_precision": round(float(average_precision_score(y_test, p_test)), 4),
            "brier": round(float(brier_score_loss(y_test, p_test)), 5),
            "operating_points": [metrics_at(y_test, p_test, t) for t in (0.5, 0.8, 0.9, 0.95)],
            "per_held_out_family": per_family,
            "note": "single-domain scores; the detector additionally requires several such domains from one host "
                    "and skips top-100k domains, which lowers false alerts further",
        },
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
    }
    out.with_suffix(".json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest["data"]["counts"], indent=2))
    print(json.dumps(manifest["test_metrics"], indent=2))


if __name__ == "__main__":
    main()
