from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client.sih26145_prod
db.models.update_one({"model_id": "iforest_host_v2"}, {"$set": {"stage": "SHADOW", "status": "EXPERIMENTAL"}, "$unset": {"accuracy": ""}})
db.models.update_one({"model_id": "xgb_window_v4"}, {"$set": {"metrics": {"precision": 0.9375, "recall": 1.0}}, "$unset": {"accuracy": ""}})
print("Registry fixed.")
