import asyncio
import uuid
import random
from datetime import datetime, timedelta, timezone

import sys
sys.path.append('.')
from backend.repositories.mongo import MongoRepository

async def populate():
    mongo = MongoRepository()
    
    # Types of threats
    threat_types = [
        {"type": "url", "chain": "PhishingURL", "desc": "Suspicious domain"},
        {"type": "email", "chain": "PhishingEmail", "desc": "BEC / Fraud"},
        {"type": "sms", "chain": "Smishing", "desc": "Urgent banking lure"},
        {"type": "qr", "chain": "Quishing", "desc": "Rogue Wi-Fi / Phishing QR"},
        {"type": "ip", "chain": "Network_Anomaly", "desc": "Zeek Port Scan"},
        {"type": "ip", "chain": "C2_Beacon", "desc": "Zeek Outbound Beacon"},
    ]
    
    now = datetime.now(timezone.utc)
    cases_to_insert = []
    
    print("Generating 250 historical cases for peaks...")
    
    for i in range(250):
        # Create a peak 2 days ago, and another 5 hours ago
        rand = random.random()
        if rand < 0.3:
            # Peak 1: 2 days ago
            time_offset = timedelta(days=2, hours=random.uniform(0, 4), minutes=random.uniform(0, 60))
        elif rand < 0.6:
            # Peak 2: 5 hours ago
            time_offset = timedelta(hours=5, minutes=random.uniform(0, 120))
        else:
            # Random spread over last 7 days
            time_offset = timedelta(days=random.uniform(0, 7))
            
        created = now - time_offset
        
        t = random.choice(threat_types)
        
        # Determine score and severity
        score = random.uniform(0.3, 0.99)
        if score > 0.8:
            sev = "CRITICAL"
        elif score > 0.6:
            sev = "HIGH"
        elif score > 0.4:
            sev = "MEDIUM"
        else:
            sev = "LOW"
            
        case = {
            "case_id": str(uuid.uuid4()),
            "source_ip": f"192.168.1.{random.randint(10, 250)}",
            "status": "CLOSED" if random.random() > 0.3 else "OPEN",
            "severity": sev,
            "risk_score": score,
            "title": f"{t['desc']} Detected",
            "threat_summary": f"Historical anomaly detected via {t['type']} channel.",
            "evidence": [],
            "alerts": [],
            "first_seen": created,
            "last_seen": created,
            "created_at": created,
            "updated_at": created,
            "detection_sources": ["historical_generator"],
            "primary_entity": f"historical_entity_{i}.com" if t['type'] != 'ip' else f"10.0.0.{random.randint(1, 255)}",
            "primary_entity_type": t['type'],
            "attack_chain": [t['chain']]
        }
        cases_to_insert.append(case)
        
    # Sort chronologically so they look like a real timeline stream in the DB
    cases_to_insert.sort(key=lambda x: x["created_at"])
    
    # Insert in batches
    if cases_to_insert:
        await mongo.cases.insert_many(cases_to_insert)
    
    print(f"Inserted {len(cases_to_insert)} historical cases with IP detections included!")

if __name__ == '__main__':
    asyncio.run(populate())
