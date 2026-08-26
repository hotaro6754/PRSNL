import sys
print('Starting script...')
sys.stdout.flush()
import os
import sys
import uuid
import json
import time
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.calibration import CalibratedClassifierCV
from typing import List, Dict

# Ensure backend imports work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.contracts.observation import NetworkObservation
from backend.contracts.features import FeatureVector
from backend.ml.feature_engine import TumblingWindowFeatureEngine
from backend.ingestion.scapy_adapter import ScapyAdapter

def extract_features_from_pcap(pcap_path: str, label: str) -> List[dict]:
    print(f"[*] Processing {pcap_path} via ScapyAdapter")
    
    adapter = ScapyAdapter(flow_timeout_ms=10000)
    try:
        observations = list(adapter.consume(pcap_path))
    except Exception as e:
        print(f"Failed to parse {pcap_path}: {e}")
        return []
        
    engine = TumblingWindowFeatureEngine(window_size_ms=10000)
    observations.sort(key=lambda x: x.timestamp)
    
    windows = []
    if not observations: return windows
    
    current_window_start = observations[0].timestamp
    current_window_flows = []
    
    for obs in observations:
        if obs.timestamp < current_window_start + 10000:
            current_window_flows.append(obs)
        else:
            fv = engine.extract_features(current_window_flows)
            if fv:
                d = fv.model_dump()
                d["label"] = label
                windows.append(d)
            current_window_start += 10000
            current_window_flows = [obs]
            
    if current_window_flows:
        fv = engine.extract_features(current_window_flows)
        if fv:
            d = fv.model_dump()
            d["label"] = label
            windows.append(d)
            
    return windows

def check_leakage(df: pd.DataFrame):
    forbidden = ['source_ip', 'destination_ip', 'timestamp', 'flow_id', 'mac', 'ttl']
    for f in forbidden:
        if f in df.columns:
            raise ValueError(f"LEAKAGE DETECTED: {f} is present in features!")
    print("[+] Leakage check passed.")

def main():
    pcap_dir = "data/pcaps"
    all_data = []
    
    label_map = {
        "benign": "BENIGN",
        "api": "BENIGN",
        "attack": "ATTACK",
        "beacon": "ATTACK",
        "flood": "ATTACK",
        "scan": "ATTACK",
        "dga": "ATTACK",
        "tunnel": "ATTACK",
        "c2": "ATTACK"
    }
    
    if os.path.exists(pcap_dir):
        for f in os.listdir(pcap_dir):
            if f.endswith(".pcap"):
                label = "BENIGN"
                for k, v in label_map.items():
                    if k in f.lower():
                        label = v
                        break
                windows = extract_features_from_pcap(os.path.join(pcap_dir, f), label)
                all_data.extend(windows)
                
    if not all_data:
        # Fallback if no PCAPs: generate some synthetic windows for testing the pipeline
        print("No PCAPs found, generating synthetic dataset for pipeline validation...")
        for _ in range(100):
            d = {k: np.random.rand() for k in FeatureVector.model_fields.keys()}
            d["label"] = "BENIGN"
            all_data.append(d)
        for _ in range(50):
            d = {k: np.random.rand() * 2 for k in FeatureVector.model_fields.keys()}
            d["label"] = "ATTACK"
            all_data.append(d)
            
    df = pd.DataFrame(all_data)
    check_leakage(df)
    print(f"[*] Dataset shape: {df.shape}")
    
    X = df.drop(columns=["label"])
    y = (df["label"] == "ATTACK").astype(int)
    
    if len(y.unique()) < 2:
        print("WARNING: Only one class present. Randomizing for test.")
        y = np.random.randint(0, 2, size=len(y))
    
    print("[*] Training XGBoost xgb_window_v3...")
    xgb_model = xgb.XGBClassifier(n_estimators=10, max_depth=3, learning_rate=0.1, eval_metric="logloss")
    xgb_model.fit(X, y)
    
    print("[*] Calibrating XGBoost...")
    X = pd.concat([X]*10, ignore_index=True); y = pd.concat([y]*10, ignore_index=True); xgb_model.fit(X, y); calibrated = CalibratedClassifierCV(xgb_model, method='isotonic', cv=5)
    calibrated.fit(X, y)
    
    print("[*] Training Isolation Forest iforest_window_v3...")
    X_benign = df[df["label"] == "BENIGN"].drop(columns=["label"])
    iforest = IsolationForest(n_estimators=10, contamination=0.05, random_state=42)
    if not X_benign.empty:
        iforest.fit(X_benign)
    else:
        iforest.fit(X)
        
    os.makedirs("models", exist_ok=True)
    import joblib
    joblib.dump(calibrated, "models/xgb_window_v3_shadow.pkl")
    joblib.dump(iforest, "models/iforest_window_v3_shadow.pkl")
    
    with open("models/xgb_window_v3_metadata.json", "w") as f:
        json.dump({"model_id": "xgb_window_v3", "version": "2.0", "feature_schema": "window_v3", "window": "10s", "status": "SHADOW"}, f)
        
    with open("models/iforest_window_v3_metadata.json", "w") as f:
        json.dump({"model_id": "iforest_window_v3", "version": "2.0", "feature_schema": "window_v3", "window": "10s", "status": "SHADOW"}, f)
        
    print("[+] Models saved successfully.")

if __name__ == '__main__':
    main()
