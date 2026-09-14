import httpx
import asyncio
import json
from datetime import datetime

async def main():
    with open("models/url_xgb_v1_metadata.json", "r") as f:
        meta = json.load(f)

    import hashlib
    with open("models/url_xgb_v1.pkl", "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    payload = {
        "model_id": "xgb_supervised",
        "model_version": "1.0.0",
        "model_type": "xgboost",
        "stage": "VALIDATING",
        "extractor_version": "1.0",
        "artifact_uri": "models/url_xgb_v1.pkl",
        "artifact_sha256": file_hash,
        "feature_schema_version": "1.0",
        "metrics": meta.get("metrics", {}),
        "created_by": "automation",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    async with httpx.AsyncClient() as client:
        print("Registering...")
        res = await client.post("http://localhost:8000/api/models/register", json=payload)
        print(res.status_code, res.text)
        
        print("Promoting...")
        res = await client.post("http://localhost:8000/api/models/xgb_supervised/versions/1.0.0/promote?stage=PRODUCTION")
        print(res.status_code, res.text)

if __name__ == "__main__":
    asyncio.run(main())
