import re

with open('backend/main.py', 'r') as f:
    content = f.read()

apis = '''

# --- Model Registry APIs ---

@app.post("/api/models/register")
async def register_model(entry: ModelRegistryEntry):
    # Enforce basic RBAC placeholder
    success = await model_registry.register_model(entry)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed (exists or error)")
    return {"status": "registered"}

@app.get("/api/models")
async def list_models():
    cursor = model_registry.collection.find({}).sort("created_at", -1).limit(50)
    models = await cursor.to_list(length=50)
    for m in models:
        m["_id"] = str(m["_id"])
    return models

@app.post("/api/models/{model_id}/versions/{version}/promote")
async def promote_model(model_id: str, version: str, stage: str, actor: str = "admin"):
    try:
        target = ModelStage(stage.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid stage")
        
    success = await model_registry.promote_model(model_id, version, target, actor, "API Promotion")
    if not success:
        raise HTTPException(status_code=400, detail="Promotion failed (not found or error)")
    return {"status": "promoted", "stage": target.value}

@app.get("/health/ml")
async def get_ml_health():
    # Return health of resolver and active models
    return {
        "xgb_supervised": {
            "production": model_resolver.caches["xgb_supervised"].production_metadata,
            "canary": model_resolver.caches["xgb_supervised"].canary_metadata,
        },
        "iforest_anomaly": {
            "production": model_resolver.caches["iforest_anomaly"].production_metadata,
            "canary": model_resolver.caches["iforest_anomaly"].canary_metadata,
        }
    }
'''

content += apis

with open('backend/main.py', 'w') as f:
    f.write(content)
