import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def evaluate_pca_iforest():
    df_train = pd.read_csv('data/df_train.csv')
    df_val = pd.read_csv('data/df_val.csv')
    df_test = pd.read_csv('data/df_test.csv')
    
    features = [c for c in df_train.columns if c not in ["label", "_pcap"]]
    X_train_benign = df_train[df_train['label'] == 'BENIGN'][features]
    y_val = (df_val['label'] == 'ATTACK').astype(int)
    y_test = (df_test['label'] == 'ATTACK').astype(int)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_benign)
    X_val_scaled = scaler.transform(df_val[features])
    X_test_scaled = scaler.transform(df_test[features])

    pca = PCA(n_components=0.90) # keep 90% variance
    X_train_pca = pca.fit_transform(X_train_scaled)
    X_val_pca = pca.transform(X_val_scaled)
    X_test_pca = pca.transform(X_test_scaled)
    
    print(f"PCA components: {X_train_pca.shape[1]}")
    
    iforest = IsolationForest(n_estimators=100, random_state=42)
    iforest.fit(X_train_pca)
    
    val_scores = iforest.score_samples(X_val_pca)
    thresh = np.percentile(val_scores[y_val==0], 5)
    
    test_scores = iforest.score_samples(X_test_pca)
    preds = (test_scores < thresh).astype(int)
    
    print(f"PCA+IForest Precision: {precision_score(y_test, preds, zero_division=0):.4f}")
    print(f"PCA+IForest Recall:    {recall_score(y_test, preds, zero_division=0):.4f}")

evaluate_pca_iforest()
