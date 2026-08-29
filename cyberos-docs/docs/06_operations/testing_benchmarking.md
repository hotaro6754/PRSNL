# Testing & Benchmarking

## T1-T15 Complete Test Guide
We validate against 15 specific network scenarios.
* **Command**: `pytest tests/test_full_regression.py`
* **Limitation**: The system successfully intercepts 11/12 malicious threats. T11 (Slow Scan) is a documented False Negative due to 10s temporal windowing.

## Performance
* **Throughput**: ~3,120 flows/sec (Containerized benchmark).
* **Latency**: ~1.40ms P50 ML Inference.