# ML Gap Analysis

## 1. Datasets & Realism
**Current State:** The ML pipeline currently relies on randomly generated synthetic numpy distributions (`train_models.py`).
**Gap:** No real network datasets (CICIDS2017, UNSW-NB15, CSE-CIC-IDS2018) have been utilized. We have not validated behavior against real PCAP/NetFlow background noise.

## 2. Feature Extraction
**Current State:** `FeatureVector` schema is rudimentary.
**Gap:** Lack of a deterministic mapping from standard academic datasets (e.g., CICFlowMeter features) backwards to our canonical `NetworkObservation`. We must ensure features can be computed passively, online, and *before* detection without active probing.

## 3. The ML Pipeline & Evidence Fusion
**Current State:** ML models were intended as standalone predictors.
**Gap:** ML must be architected as *evidence*. There is no Model Router, Calibration layer, or Evidence Fusion engine to intelligently merge deterministic rule hits with ML anomaly/probability scores.

## 4. MLOps & Lineage
**Current State:** Models are static `.pkl` files with no traceability.
**Gap:** No model registry, no tracking of `feature_schema_version`, and no drift monitoring. (Note: `MLPrediction` contract was recently updated in P0 to require this lineage, but the infrastructure to populate it doesn't exist yet).

## 5. Data Leakage Precautions
**Current State:** None.
**Gap:** No automated testing for temporal, host-level, or cross-dataset leakage. We must implement file-based and time-based holdouts to ensure models aren't just memorizing IP addresses or exact timestamps.
