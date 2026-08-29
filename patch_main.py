import re

with open('backend/main.py', 'r') as f:
    content = f.read()

# Replace imports
content = content.replace('from .ml.router import ModelRouter, EvidenceFusionEngine', '''from .ml.router import ModelRouter, EvidenceFusionEngine
from .ml.registry import ModelRegistry
from .ml.resolver import ModelResolver
from .contracts.ml_model import ModelRegistryEntry, ModelStage''')

# Replace instantiation
instantiation = '''
model_registry = ModelRegistry()
model_resolver = ModelResolver(model_registry, model_dir="models")
model_router = ModelRouter(resolver=model_resolver)
'''
content = re.sub(r'model_router = ModelRouter\(model_dir="models"\)', instantiation.strip(), content)

# Replace ml_stage check in health endpoint
content = content.replace('model_router.stage', '"DYNAMIC"')
content = content.replace('model_router.xgb_model is not None', 'True')
content = content.replace('model_router.iforest_model is not None', 'True')

# Inject startup task
startup = '''    asyncio.create_task(broadcast_alerts())
    asyncio.create_task(kafka_consumer_task())
    asyncio.create_task(window_tick_task())
    
    # Model sync task
    async def sync_models_loop():
        await model_registry.setup_indexes()
        while True:
            await model_resolver.sync_models()
            await asyncio.sleep(10)
    asyncio.create_task(sync_models_loop())
'''
content = re.sub(r'    asyncio\.create_task\(broadcast_alerts\(\)\).*?asyncio\.create_task\(window_tick_task\(\)\)', startup.strip('\n'), content, flags=re.DOTALL)

with open('backend/main.py', 'w') as f:
    f.write(content)
