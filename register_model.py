import os
import hashlib
from datetime import datetime, timezone
from pymongo import MongoClient

model_path = 'models/xgb_window_v5.pkl'
with open(model_path, 'rb') as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()

client = MongoClient('mongodb://localhost:27017/')
db = client['ndr_database']

doc = {
    'model_id': 'xgb_window_v5',
    'model_version': '5.0.0',
    'model_type': 'xgb_supervised',
    'stage': 'PRODUCTION',
    'feature_schema_version': '1.0',
    'extractor_version': '1.0',
    'artifact_uri': 'file:///app/backend/../models/xgb_window_v5.pkl',
    'artifact_sha256': sha256,
    'created_at': datetime.now(timezone.utc),
    'metrics': {},
    'owner': 'system',
    'deployment_config': {}
}

db.model_registry.update_one(
    {'model_id': 'xgb_window_v5', 'model_version': '5.0.0'},
    {'$set': doc},
    upsert=True
)
print('Model registered successfully!')
