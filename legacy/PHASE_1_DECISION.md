# Phase 1 Decision: ML Strategy & Dataset Selection

## 1. Datasets Selected
* **Base Training**: **CICIDS2017** and **UNSW-NB15**.
* **Cross-Validation / OOD Testing**: **CSE-CIC-IDS2018** and **CICIoT2023**.
* **Why**: We must train on one network topology (CICIDS) and test on a completely different one (UNSW-NB15) to prove the model has learned generic malicious behaviors (e.g., the mathematical shape of a port scan) rather than the specific IP addresses or TTLs of the CICIDS lab.

## 2. Datasets Rejected
* **KDD99 / NSL-KDD**: Completely obsolete. Network traffic from 1999 does not represent modern TLS-heavy, high-bandwidth enterprise traffic.
* **CTU-13**: Outdated background traffic, heavily focused on legacy botnets.

## 3. The Online Feature Contract
We explicitly reject offline-only features. The ML model will consume a vector derived *strictly* from tumbling windows over `NetworkObservation`:
* Window Duration (sec)
* Fwd/Bwd Packet Count
* Fwd/Bwd Byte Count
* Fwd/Bwd Packet Length (Mean, Std, Max, Min)
* Inter-Arrival Time (IAT) Mean/Std (computed intra-window)
* Protocol/TCP Flag Distributions
* TLS JA3 (Categorical/Embedded)
* DNS SLD Entropy

**Critical Rule:** IP Addresses, MAC Addresses, Source Ports, and TTLs are **blacklisted** from the training vector to prevent identity leakage and tool-artifact memorization.

## 4. Candidate Models
* **Supervised (Level 1)**: **LightGBM** (or XGBoost). Chosen for sub-millisecond streaming inference, small memory footprint, and native TreeSHAP explainability.
* **Anomaly (Level 2)**: **Isolation Forest**. Chosen for OOD detection and zero-day hunting without requiring dense neural networks.

## 5. Leakage Controls
1. **Time-Series Splitting**: No random `train_test_split`. Data must be split sequentially by time to prevent future-to-past leakage.
2. **Feature Blacklisting**: (See Section 3).
3. **Data Plane Parity**: We will not train on the CSVs provided by the universities. We will run the raw PCAPs through our own `ZeekAdapter` to generate the training data. This guarantees that what the model learns is exactly what the streaming data plane will provide in production.

## 6. Calibration Strategy
Raw outputs from LightGBM are not probabilities. We will apply **Platt Scaling (Logistic Calibration)** or **Isotonic Regression** on a held-out validation set so that when the model outputs "0.85", it actually means there is an 85% real-world probability of malice.

## 7. Shadow-Mode Strategy
The ML engine will initially deploy in **Shadow Mode**. 
- It will consume Kafka streams and generate `MLPrediction` objects.
- It will *not* trigger `SecurityCase` escalations on its own.
- The UI will display ML predictions alongside deterministic alerts for human analysts to evaluate ("Ghost Alerts").

## 8. What NOT to Implement
- **Do not** implement Deep Learning / LSTMs. They are too slow for this streaming budget and too hard to explain to a SOC analyst.
- **Do not** modify the deterministic engine. The ML pipeline is an *addition* (Evidence Fusion), not a replacement.
- **Do not** train on the university-provided CSV files.

## 9. Recommended Training Order (Phase 2 & 3)
1. Write the PySpark/Pandas script to convert `NetworkObservation` logs into the `FeatureVector` matrix.
2. Stream the CICIDS2017 PCAP through `ZeekAdapter` to generate the raw dataset.
3. Train LightGBM.
4. Stream the UNSW-NB15 PCAP through `ZeekAdapter`. Evaluate the LightGBM model on it (Cross-Domain Validation).
