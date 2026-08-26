from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["sih26145_prod"]
cases = db.security_cases.find().sort("created_at", -1).limit(10)
for c in cases:
    print(f"[{c['created_at']}] Case: {c['title']} | Threat: {c.get('threat_summary', '')} | Conf: {c.get('risk_score', 'N/A')}")
    for alert in c.get("alerts", []):
        print(f"  Alert: {alert.get('threat_class')} from {alert.get('detector_id')}")
