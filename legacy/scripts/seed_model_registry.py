import asyncio
from backend.ml.registry import ModelRegistry
from backend.contracts.ml_model import ModelRegistryEntry, ModelStage
import os
import hashlib
from datetime import datetime, timezone

def get_hash(path):
    if not os.path.exists(path):
        return "not_found"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

async def main():
    registry = ModelRegistry("mongodb://localhost:27017")
    await registry.setup_indexes()

    await registry.collection.delete_many({})

    xgb_entry = ModelRegistryEntry(
        model_id="xgb_window_v5",
        model_version="5.0.0",
        model_type="xgb_supervised",
        stage=ModelStage.PRODUCTION,
        artifact_uri="models/xgb_window_v5.pkl",
        artifact_sha256=get_hash("models/xgb_window_v5.pkl"),
        feature_schema_version="1.0",
        extractor_version="1.0",
        created_at=datetime.now(timezone.utc),
        deployed_at=datetime.now(timezone.utc),
        metrics={"accuracy": 0.95},
        deployment_config={"canary_percent": 100.0}
    )

    iforest_entry = ModelRegistryEntry(
        model_id="iforest_host_v2",
        model_version="2.0.0",
        model_type="iforest_anomaly",
        stage=ModelStage.PRODUCTION,
        artifact_uri="models/iforest_host_v2.pkl",
        artifact_sha256=get_hash("models/iforest_host_v2.pkl"),
        feature_schema_version="1.0",
        extractor_version="1.0",
        created_at=datetime.now(timezone.utc),
        deployed_at=datetime.now(timezone.utc),
        metrics={"accuracy": 0.90},
        deployment_config={"canary_percent": 100.0}
    )

    await registry.register_model(xgb_entry)
    await registry.register_model(iforest_entry)
    print("Models registered successfully!")

asyncio.run(main())
