import asyncio
from backend.contracts.ml_model import ModelStage
from backend.ml.registry import ModelRegistry
from backend.ml.resolver import ModelResolver

async def main():
    registry = ModelRegistry('mongodb://localhost:27017')
    resolver = ModelResolver(registry, 'models')
    
    # 1. Update deployment config and promote to Canary
    v5 = await registry.get_model('xgb_supervised_v5', '5.0.0')
    
    await registry.collection.update_one(
        {'model_id': 'xgb_supervised_v5', 'model_version': '5.0.0'},
        {'\x24set': {'deployment_config': {'canary_percent': 50}}}
    )
    
    await registry.promote_model('xgb_supervised_v5', '5.0.0', ModelStage.CANARY, 'system', 'Test Canary')
    print('V5 Promoted to CANARY (50%)')
    
    # 2. Sync Resolver
    await resolver.sync_models()
    
    # 3. Test Routing
    ips = [f"192.168.1.{i}" for i in range(100)]
    v4_count = 0
    v5_count = 0
    
    for ip in ips:
        model, meta, _ = resolver.get_routing('xgb_supervised', ip)
        if meta.model_version == '4.0.0':
            v4_count += 1
        elif meta.model_version == '5.0.0':
            v5_count += 1
            
    print(f"Routing results for 100 IPs -> V4: {v4_count}, V5: {v5_count}")
    
if __name__ == '__main__':
    asyncio.run(main())
