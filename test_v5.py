import asyncio
import hashlib
from datetime import datetime, timezone
from backend.contracts.ml_model import ModelRegistryEntry, ModelStage
from backend.ml.registry import ModelRegistry
from backend.ml.resolver import ModelResolver

async def main():
    registry = ModelRegistry('mongodb://localhost:27017')
    resolver = ModelResolver(registry, 'models')
    
    import os
    sha = hashlib.sha256()
    with open('models/xgb_window_v4.pkl', 'rb') as f:
        for b in iter(lambda: f.read(4096), b''):
            sha.update(b)
            
    v5_entry = ModelRegistryEntry(
        model_id='xgb_supervised_v5',
        model_version='5.0.0',
        model_type='xgb_supervised',
        stage=ModelStage.SHADOW,
        feature_schema_version='1.0',
        extractor_version='1.0',
        artifact_uri='models/xgb_window_v4.pkl',
        artifact_sha256=sha.hexdigest(),
        created_at=datetime.now(timezone.utc)
    )
    
    await registry.register_model(v5_entry, 'system')
    print('V5 Registered in MongoDB as SHADOW')
    
    await resolver.sync_models()
    
    prod, pmeta, _ = resolver.get_routing('xgb_supervised', 'ip')
    shadow, smeta = resolver.get_shadow('xgb_supervised')
    
    print(f'Active Prod: {pmeta.model_version if pmeta else "None"}')
    print(f'Active Shadow: {smeta.model_version if smeta else "None"}')
    
if __name__ == '__main__':
    asyncio.run(main())
