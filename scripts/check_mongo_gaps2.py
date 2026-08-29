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

client = MongoClient("mongodb://localhost:27017/")
db = client["cyberos_prod"]

print("--- RECENT CASES ---")
cases = db.security_cases.find().sort("created_at", -1).limit(50)
found_exfil = False
found_udp = False
for c in cases:
    threat_sum = c.get('threat_summary', '')
    title = c.get('title', '')
    if "Exfiltration" in threat_sum or "EXFILTRATION" in threat_sum:
        found_exfil = True
    for alert in c.get("alerts", []):
        tc = alert.get('threat_class', '')
        if "Exfiltration" in tc or "EXFILTRATION" in tc:
            found_exfil = True
            print(f"[{c['created_at']}] Case: {title} | Threat: {threat_sum} | Conf: {c.get('risk_score', 'N/A')}")
            print(f"  Alert: {tc} from {alert.get('detector_id')}")
            for ev in alert.get("evidence", []):
                print(f"    Evidence: {ev.get('feature')} = {ev.get('value')}")
        if "UDP" in tc or tc == "DDoS":
            for ev in alert.get("evidence", []):
                if ev.get("feature") == "udp_ratio" and float(ev.get("value", 0)) > 0:
                    found_udp = True
                    print(f"[{c['created_at']}] Case: {title} | Threat: {threat_sum} | Conf: {c.get('risk_score', 'N/A')}")
                    print(f"  Alert: {tc} from {alert.get('detector_id')}")
                    print(f"    Evidence: {ev.get('feature')} = {ev.get('value')}")

if not found_exfil:
    print("NO EXFIL CASES FOUND.")
if not found_udp:
    print("NO UDP REFLECTION CASES FOUND.")
