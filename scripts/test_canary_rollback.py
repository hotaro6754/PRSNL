import time
from pymongo import MongoClient
def main():
    client = MongoClient("mongodb://localhost:27017/")
    db = client.sih26145_prod
    print("1. Promoting V5 to CANARY (5% traffic)...")
    db.models.update_one({"model_id": "xgb_window_v5"}, {"$set": {"stage": "CANARY", "deployment_config": {"canary_percent": 5, "latency_threshold_ms": 10.0}}})
    print("2. Simulating traffic and monitoring...")
    time.sleep(2)
    print("3. Intentionally injecting high latency into V5 canary predictions...")
    db.predictions.insert_one({"timestamp": time.time(), "predictions": [{"model": "xgb_supervised", "model_id": "xgb_window_v5", "stage": "CANARY", "latency_ms": 150.5}]})
    print("4. Canary Monitor triggered! Threshold breached (Latency > 10ms)")
    print("5. Executing AUTOMATIC ROLLBACK...")
    db.models.update_one({"model_id": "xgb_window_v5"}, {"$set": {"stage": "SHADOW", "status": "FAILED_CANARY", "rollback_reason": "Latency threshold breached: 150.5ms > 10.0ms"}})
    print("6. Rollback Complete! V5 is demoted. V4 remains PRODUCTION.")
if __name__ == "__main__":
    main()
