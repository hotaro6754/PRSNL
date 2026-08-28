import os
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, roc_auc_score, brier_score_loss
import joblib
import json
from datetime import datetime

output_dir = 'models'

def train():
    print("Generating controlled ML fixture data for URL training...")
    np.random.seed(42)
    n = 5000
    df = pd.DataFrame({
        'lex_domain_entropy': np.random.normal(3.0, 0.5, n),
        'lex_total_length': np.random.normal(40, 20, n),
        'lex_numeric_ratio': np.random.beta(2, 5, n),
        'domain_has_hex_pattern': np.random.choice([0.0, 1.0], n, p=[0.9, 0.1]),
        'struct_num_subdomains': np.random.poisson(1, n),
        'domain_has_suspicious_tld': np.random.choice([0.0, 1.0], n, p=[0.95, 0.05]),
        'struct_has_ip_in_domain': np.random.choice([0.0, 1.0], n, p=[0.99, 0.01]),
        'behav_brand_spoofing': np.random.choice([0.0, 1.0], n, p=[0.9, 0.1]),
        'label': np.random.choice([0, 1], n)
    })
    # Add correlation so the model learns something real
    df.loc[df['label'] == 1, 'lex_domain_entropy'] += 1.5
    df.loc[df['label'] == 1, 'lex_total_length'] += 40
    df.loc[df['label'] == 1, 'struct_has_ip_in_domain'] = np.random.choice([0.0, 1.0], sum(df['label'] == 1), p=[0.8, 0.2])
    df.loc[df['label'] == 1, 'domain_has_suspicious_tld'] = np.random.choice([0.0, 1.0], sum(df['label'] == 1), p=[0.5, 0.5])

    features = [
        'lex_domain_entropy', 'lex_total_length', 'lex_numeric_ratio', 
        'domain_has_hex_pattern', 'struct_num_subdomains', 'domain_has_suspicious_tld', 
        'struct_has_ip_in_domain', 'behav_brand_spoofing'
    ]
    
    X = df[features]
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training XGBoost Classifier...")
    xgb = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, eval_metric="logloss")
    
    print("Calibrating Probabilities (Isotonic Regression)...")
    calibrated_xgb = CalibratedClassifierCV(xgb, method='isotonic', cv=3)
    calibrated_xgb.fit(X_train, y_train)

    print("Evaluating Model...")
    y_pred = calibrated_xgb.predict(X_test)
    y_prob = calibrated_xgb.predict_proba(X_test)[:, 1]

    print("\n--- ML Evaluation Report ---")
    print(classification_report(y_test, y_pred))
    
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(calibrated_xgb, os.path.join(output_dir, "url_xgb_v1.pkl"))
    
    metadata = {
        "model_id": "url_xgb",
        "version": "v1.0",
        "training_timestamp": datetime.now().isoformat(),
        "feature_schema": features,
        "metrics": {
            "roc_auc": float(roc_auc_score(y_test, y_prob)),
            "brier_score": float(brier_score_loss(y_test, y_prob))
        }
    }
    with open(os.path.join(output_dir, "url_xgb_v1_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Model saved to {output_dir}/url_xgb_v1.pkl")

if __name__ == '__main__':
    train()
