#!/usr/bin/env python3
"""
Seed realistic NTRO PS #26145 Unidirectional IP Network Incidents into MongoDB.
Strictly zero phishing, zero SMS, zero email, zero QR codes.
All records represent passive observation across a hardware data diode / optical tap.
"""

import uuid
from datetime import datetime, timezone, timedelta
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["cyberos"]

# Ensure any leftover non-network records are purged
db.cases.delete_many({
    "$or": [
        {"primary_entity_type": {"$in": ["url", "email", "sms", "qr", "URL", "EMAIL", "SMS", "QR"]}},
        {"title": {"$regex": "URL|SMS|EMAIL|QR|Phish|Smish|Quish", "$options": "i"}},
        {"primary_entity": {"$regex": "http|Elon|ETH|URGENT|PayPal|apple|bit.ly|SMS|EMAIL|QR", "$options": "i"}}
    ]
})
db.alerts.delete_many({
    "$or": [
        {"category": {"$in": ["content_scan", "url", "email", "sms", "qr"]}},
        {"threat_class": {"$regex": "URL|SMS|EMAIL|QR|Phish|Smish|Quish", "$options": "i"}}
    ]
})

NTRO_VECTORS = [
    {
        "class": "Volumetric SYN Flood (DDoS)",
        "chain": ["VOLUMETRIC_DOS", "SYN_FLOOD", "ENTROPY_ANOMALY"],
        "severity": "CRITICAL",
        "score": 96,
        "src_prefix": "185.220.101.",
        "dst_prefix": "10.0.1.",
        "rationale": "High PPS burst (1,420 pps) with elevated Source-IP Shannon entropy (H=3.68) across simplex optical tap without reverse SYN-ACK."
    },
    {
        "class": "Botnet C2 Beaconing",
        "chain": ["BEACONING", "C2_CHANNEL", "PERIODIC_DELTA"],
        "severity": "HIGH",
        "score": 88,
        "src_prefix": "45.154.255.",
        "dst_prefix": "10.0.2.",
        "rationale": "Robotic periodic heartbeat detected across unidirectional stream with low IAT Coefficient of Variation (CV=0.018)."
    },
    {
        "class": "DNS Covert Tunnel / DGA",
        "chain": ["DNS_TUNNEL", "DGA_APEX", "SUBDOMAIN_ENTROPY"],
        "severity": "CRITICAL",
        "score": 94,
        "src_prefix": "91.240.118.",
        "dst_prefix": "10.0.3.",
        "rationale": "Unidirectional DNS exfiltration identified via character entropy analysis (H=4.85) across 32 unique subdomains under a single apex."
    },
    {
        "class": "Encrypted Session Metadata Anomaly",
        "chain": ["ENCRYPTED_ANOMALY", "TLS_METADATA", "JA3_FINGERPRINT"],
        "severity": "HIGH",
        "score": 85,
        "src_prefix": "194.26.135.",
        "dst_prefix": "10.0.4.",
        "rationale": "Malicious JA3 fingerprint (72a5893e05bc431486873cb167db0707) and anomalous packet size transitions detected without payload decryption."
    },
    {
        "class": "Port Scan (Reconnaissance)",
        "chain": ["PORT_SCAN", "RECONNAISSANCE", "FAN_OUT_CARDINALITY"],
        "severity": "CRITICAL",
        "score": 92,
        "src_prefix": "23.129.64.",
        "dst_prefix": "10.0.1.",
        "rationale": "Destination fan-out cardinality threshold exceeded with 128 destination ports probed in 10-second tumbling window."
    },
    {
        "class": "Asymmetric Data Exfiltration",
        "chain": ["DATA_EXFILTRATION", "ASYMMETRIC_VOLUME", "SIMPLEX_EGRESS"],
        "severity": "HIGH",
        "score": 90,
        "src_prefix": "192.168.1.",
        "dst_prefix": "10.0.5.",
        "rationale": "Heavy asymmetric outbound volume (42.8 MB) with 0 inbound return packets confirming unauthorized simplex bulk exfiltration."
    }
]

now = datetime.now(timezone.utc)
seeded_cases = []
seeded_alerts = []

for idx in range(30):
    vec = NTRO_VECTORS[idx % len(NTRO_VECTORS)]
    time_offset = timedelta(minutes=(30 - idx) * 3, seconds=idx * 7)
    case_time = (now - time_offset).isoformat()
    case_id = str(uuid.uuid4())
    
    src_ip = f"{vec['src_prefix']}{(idx * 7 + 11) % 240 + 10}"
    dst_ip = f"{vec['dst_prefix']}{(idx * 3 + 5) % 240 + 10}"
    flow_desc = f"{src_ip} -> {dst_ip}"
    
    alert = {
        "alert_id": case_id,
        "timestamp": case_time,
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "threat_class": vec["class"],
        "severity": vec["severity"],
        "confidence": round(vec["score"] / 100.0, 2),
        "detector_id": f"NTRO-SENTINEL-{vec['chain'][0]}",
        "category": "unidirectional_network_flow",
        "evidence": [
            {"feature": "simplex_link", "value": "OPTICAL_TAP", "explanation": "Ingress across unidirectional hardware data diode (0 ACKs)"},
            {"feature": "threat_rationale", "value": vec["chain"][0], "explanation": vec["rationale"]},
            {"feature": "risk_score", "value": vec["score"], "explanation": "Calculated Bayesian fused confidence metric"}
        ]
    }
    
    case = {
        "case_id": case_id,
        "organization_id": "tenant-1",
        "primary_entity": flow_desc,
        "primary_entity_type": "ip_flow",
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "status": "OPEN",
        "severity": vec["severity"],
        "risk_score": vec["score"],
        "title": f"Unidirectional Threat: {vec['class']}",
        "threat_summary": vec["class"],
        "attack_chain": vec["chain"],
        "alerts": [alert],
        "first_seen": case_time,
        "last_seen": case_time,
        "created_at": case_time,
        "updated_at": case_time
    }
    
    seeded_cases.append(case)
    seeded_alerts.append(alert)

db.cases.insert_many(seeded_cases)
db.alerts.insert_many(seeded_alerts)

print(f"Successfully seeded {len(seeded_cases)} authentic NTRO PS #26145 network threat cases into MongoDB.")
print(f"Total cases in DB: {db.cases.count_documents({})}")
print(f"Total alerts in DB: {db.alerts.count_documents({})}")
