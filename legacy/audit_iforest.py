import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, roc_auc_score, average_precision_score
from sklearn.preprocessing import StandardScaler, RobustScaler
import joblib

from train_window_v4 import extract_dataset, check_leakage
from backend.contracts.features import FeatureVector

def load_data():
    if os.path.exists('data/df_train.csv'):
        print('Loading cached CSVs...')
        df_train = pd.read_csv('data/df_train.csv')
        df_val = pd.read_csv('data/df_val.csv')
        df_test = pd.read_csv('data/df_test.csv')
        return df_train, df_val, df_test

    print('Extracting from PCAPs...')
    pcap_dir = "data/pcaps"
    all_pcaps = [os.path.join(pcap_dir, f) for f in os.listdir(pcap_dir) if f.endswith(".pcap")]
    label_map = {
        "benign": "BENIGN", "api": "BENIGN", "attack": "ATTACK", "beacon": "ATTACK", 
        "flood": "ATTACK", "scan": "ATTACK", "dga": "ATTACK", "tunnel": "ATTACK", "c2": "ATTACK"
    }
    train_pcaps = [p for p in all_pcaps if any(x in p for x in ['web', 'dns', 'syn_flood', 'real_port_scan'])]
    val_pcaps = [p for p in all_pcaps if any(x in p for x in ['api', 'udp_flood', 'dga_botnet'])]
    test_pcaps = [p for p in all_pcaps if any(x in p for x in ['transfer', 'stealth_scan', 'encrypted_c2'])]
    
    df_train = extract_dataset(train_pcaps, label_map)
    df_val = extract_dataset(val_pcaps, label_map)
    df_test = extract_dataset(test_pcaps, label_map)
    
    df_train.to_csv('data/df_train.csv', index=False)
    df_val.to_csv('data/df_val.csv', index=False)
    df_test.to_csv('data/df_test.csv', index=False)
    return df_train, df_val, df_test

df_train, df_val, df_test = load_data()
features = [c for c in df_train.columns if c not in ["label", "_pcap"]]

X_train_benign = df_train[df_train['label'] == 'BENIGN'][features]
y_val = (df_val['label'] == 'ATTACK').astype(int)
y_test = (df_test['label'] == 'ATTACK').astype(int)

print(f"Benign Train Samples: {len(X_train_benign)}")
print(f"Val Samples: {len(y_val)} (Attacks: {y_val.sum()})")
print(f"Test Samples: {len(y_test)} (Attacks: {y_test.sum()})")

# 1. Baseline Isolation Forest (Current)
print('\n--- 1. Current Baseline IForest ---')
iforest = IsolationForest(n_estimators=50, contamination=0.05, random_state=42)
iforest.fit(X_train_benign)
preds = np.where(iforest.predict(df_test[features]) == 1, 0, 1)
print(f"Precision: {precision_score(y_test, preds, zero_division=0):.4f}")
print(f"Recall:    {recall_score(y_test, preds, zero_division=0):.4f}")

# 2. Score distributions
val_scores = iforest.score_samples(df_val[features])
test_scores = iforest.score_samples(df_test[features])
print(f"Val Benign Score Mean: {val_scores[y_val==0].mean():.4f}, Attack Score Mean: {val_scores[y_val==1].mean():.4f}")
print(f"Test Benign Score Mean: {test_scores[y_test==0].mean():.4f}, Attack Score Mean: {test_scores[y_test==1].mean():.4f}")

# 3. Robust Scaler + Robust Z-Score Baseline
print('\n--- 3. Robust Z-Score Baseline (Mahalanobis approx on independent features) ---')
scaler = RobustScaler()
scaler.fit(X_train_benign)
X_val_scaled = scaler.transform(df_val[features])
X_test_scaled = scaler.transform(df_test[features])

# Simple anomaly score = max absolute z-score across all features
val_z_scores = np.max(np.abs(X_val_scaled), axis=1)
test_z_scores = np.max(np.abs(X_test_scaled), axis=1)

print(f"Val Z-Score Benign Mean: {val_z_scores[y_val==0].mean():.4f}, Attack Mean: {val_z_scores[y_val==1].mean():.4f}")
print(f"Test Z-Score Benign Mean: {test_z_scores[y_test==0].mean():.4f}, Attack Mean: {test_z_scores[y_test==1].mean():.4f}")

# Choose threshold on validation set for 5% FPR
benign_val_z = val_z_scores[y_val==0]
if len(benign_val_z) > 0:
    thresh_z = np.percentile(benign_val_z, 95)
    preds_z = (test_z_scores > thresh_z).astype(int)
    print(f"Z-Score Threshold (95th pctile val): {thresh_z:.4f}")
    print(f"Z-Score Precision: {precision_score(y_test, preds_z, zero_division=0):.4f}")
    print(f"Z-Score Recall:    {recall_score(y_test, preds_z, zero_division=0):.4f}")

# 4. IForest with Subselected Features (XGBoost Top Features)
print('\n--- 4. IForest with Top Features ---')
top_features = ['window_duration', 'packet_count', 'udp_ratio', 'packet_size_mean', 'host_bytes_out_5m']
top_features = [f for f in top_features if f in features]
iforest_top = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
iforest_top.fit(X_train_benign[top_features])

# Evaluate based on score threshold tuned on Val
val_scores_top = iforest_top.score_samples(df_val[top_features])
if len(val_scores_top[y_val==0]) > 0:
    thresh_iforest = np.percentile(val_scores_top[y_val==0], 5) # 5th percentile because lower is anomalous
    
    test_scores_top = iforest_top.score_samples(df_test[top_features])
    preds_top = (test_scores_top < thresh_iforest).astype(int)
    print(f"IForest Top-Feat Threshold: {thresh_iforest:.4f}")
    print(f"IForest Top-Feat Precision: {precision_score(y_test, preds_top, zero_division=0):.4f}")
    print(f"IForest Top-Feat Recall:    {recall_score(y_test, preds_top, zero_division=0):.4f}")

