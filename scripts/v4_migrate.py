import asyncio
import os
import hashlib
from datetime import datetime, timezone
from backend.ml.registry import ModelRegistry
from backend.contracts.ml_model import ModelRegistryEntry, ModelStage

async def migrate_v4():
    registry = ModelRegistry(mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    await registry.setup_indexes()
    
    # We will generate a SHA256 of the actual model files if they exist locally
    def get_hash(path):
        if os.path.exists(path):
            sha256_hash = hashlib.sha256()
            with open(path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        return hashlib.sha256(b"mock").hexdigest()
        
    xgb_sha = get_hash("models/xgb_window_v4.pkl")
    if_sha = get_hash("models/iforest_host_v2.pkl")
    
    xgb_entry = ModelRegistryEntry(
        model_id="xgb_supervised_baseline",
        model_version="4.0.0",
        model_type="xgb_supervised",
        stage=ModelStage.PRODUCTION,
        feature_schema_version="1.0",
        extractor_version="1.0",
        artifact_uri="models/xgb_window_v4.pkl",
        artifact_sha256=xgb_sha,
        created_at=datetime.now(timezone.utc),
        deployed_at=datetime.now(timezone.utc),
        owner="v4_migration",
        deployment_config={}
    )
    
    if_entry = ModelRegistryEntry(
        model_id="iforest_anomaly_baseline",
        model_version="2.0.0",
        model_type="iforest_anomaly",
        stage=ModelStage.SHADOW,
        feature_schema_version="1.0",
        extractor_version="1.0",
        artifact_uri="models/iforest_host_v2.pkl",
        artifact_sha256=if_sha,
        created_at=datetime.now(timezone.utc),
        deployed_at=datetime.now(timezone.utc),
        owner="v4_migration",
        deployment_config={}
    )
    
    await registry.register_model(xgb_entry, actor="system", reason="V4 Baseline Migration")
    await registry.register_model(if_entry, actor="system", reason="V4 Baseline Migration")
    print("V4 Models Migrated to Registry")

if __name__ == '__main__':
    asyncio.run(migrate_v4())
