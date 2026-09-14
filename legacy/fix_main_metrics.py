import re

with open('backend/main.py', 'r') as f:
    code = f.read()

# Add the /api/ml/metrics endpoint
ml_endpoint = """
@app.get("/api/ml/metrics")
async def get_ml_metrics():
    import json
    import os
    metadata_path = os.path.join(os.path.dirname(__file__), '../models/url_xgb_v1_metadata.json')
    try:
        with open(metadata_path, 'r') as f:
            meta = json.load(f)
        return meta
    except Exception as e:
        return {"error": str(e)}
"""
if "/api/ml/metrics" not in code:
    code += ml_endpoint

with open('backend/main.py', 'w') as f:
    f.write(code)
print("Added /api/ml/metrics to main.py")
