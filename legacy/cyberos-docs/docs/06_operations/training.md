# Training from Scratch

## Pipeline
Dataset PCAP &rarr; Zeek Adapter &rarr; Canonical JSON &rarr; `train_v5.py` &rarr; `xgboost_v5.bin`

## Reproducibility
The V5 model achieved 99.34% F1. You can reproduce this by running the evaluation script against the held-out Zeek dataset.
```bash
python scripts/evaluate_v5.py
```