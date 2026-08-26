import joblib
import os
from backend.ml.dummy import DummyXGB, DummyIForest

os.makedirs('models', exist_ok=True)
joblib.dump(DummyXGB(), 'models/xgb_window_v4.pkl')
joblib.dump(DummyIForest(), 'models/iforest_host_v2.pkl')
