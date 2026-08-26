from pymongo import MongoClient
import json
from datetime import datetime

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "uuid"):
            return str(obj)
        return str(obj)

client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["ps26145"]

print("--- RECENT CASES ---")
cases = db.security_cases.find().sort("created_at", -1).limit(10)
for c in cases:
    print(f"[{c['created_at']}] Case: {c['title']} | Threat: {c.get('threat_summary', '')} | Conf: {c.get('risk_score', 'N/A')}")
    for alert in c.get("alerts", []):
        print(f"  Alert: {alert.get('threat_class')} from {alert.get('detector_id')}")
        for ev in alert.get("evidence", []):
            if ev.get("feature") in ["asymmetry_ratio", "udp_ratio", "outbound_bytes"]:
                print(f"    Evidence: {ev.get('feature')} = {ev.get('value')}")
