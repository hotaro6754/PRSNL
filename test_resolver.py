import asyncio
from backend.ml.registry import ModelRegistry
from backend.ml.resolver import ModelResolver

async def main():
    registry = ModelRegistry('mongodb://localhost:27017')
    resolver = ModelResolver(registry, 'models')
    
    print('Syncing models from MongoDB...')
    await resolver.sync_models()
    
    xgb_prod, xgb_meta, _ = resolver.get_routing('xgb_supervised', '127.0.0.1')
    print(f'XGB Prod Version: {xgb_meta.model_version if xgb_meta else "None"}')
    print(f'XGB Prod Stage: {xgb_meta.stage.value if xgb_meta else "None"}')
    
    if_prod, if_meta, _ = resolver.get_routing('iforest_anomaly', '127.0.0.1')
    if_shadow, if_shadow_meta = resolver.get_shadow('iforest_anomaly')
    
    print(f'IForest Prod: {if_meta.model_version if if_meta else "None"}')
    print(f'IForest Shadow: {if_shadow_meta.model_version if if_shadow_meta else "None"}')
    
if __name__ == '__main__':
    asyncio.run(main())
