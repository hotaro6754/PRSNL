from pymongo import MongoClient

def main():
    client = MongoClient("mongodb://localhost:27017")
    db = client["sih26145_prod"]
    alerts = list(db.alerts.find().sort("timestamp", -1).limit(10))
    if alerts:
        print(f"Found {len(alerts)} recent alerts:")
        for alert in alerts:
            print(f" - {alert.get('timestamp')} | {alert.get('threat_class')} | {alert.get('source_ip')} -> {alert.get('destination_ip')} | {alert.get('detector_id')} | conf: {alert.get('confidence')}")
    else:
        print("No alerts found in MongoDB.")

if __name__ == "__main__":
    main()
