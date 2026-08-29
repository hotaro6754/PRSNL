import os
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
import joblib

output_dir = 'models'

def train_sms():
    print("Generating controlled ML fixture data for SMS training...")
    np.random.seed(42)
    n = 2000
    df = pd.DataFrame({
        'sms_length': np.random.normal(80, 40, n),
        'sms_num_urls': np.random.poisson(0.5, n),
        'sms_scam_keyword_count': np.random.poisson(0.2, n),
        'sms_urgency_score': np.random.beta(2, 5, n),
        'sms_highest_url_risk': np.random.beta(1, 10, n),
        'label': np.random.choice([0, 1], n)
    })
    # Add correlation
    df.loc[df['label'] == 1, 'sms_scam_keyword_count'] += np.random.poisson(2, sum(df['label'] == 1))
    df.loc[df['label'] == 1, 'sms_highest_url_risk'] = np.random.beta(5, 2, sum(df['label'] == 1))
    df.loc[df['label'] == 1, 'sms_urgency_score'] += 0.4
    
    features = [
        'sms_length', 'sms_num_urls', 'sms_scam_keyword_count', 
        'sms_urgency_score', 'sms_highest_url_risk'
    ]
    
    X = df[features]
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    xgb = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, eval_metric="logloss")
    calibrated_xgb = CalibratedClassifierCV(xgb, method='isotonic', cv=3)
    calibrated_xgb.fit(X_train, y_train)

    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(calibrated_xgb, os.path.join(output_dir, "sms_xgb_v1.pkl"))
    print("Saved sms_xgb_v1.pkl")

if __name__ == '__main__':
    train_sms()
