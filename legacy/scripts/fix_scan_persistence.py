import re

with open('backend/main.py', 'r') as f:
    content = f.read()

# Let's insert the case saving logic before 'return final_result'
case_save_logic = """
    try:
        from backend.contracts.case import CyberCase
        
        # Build the case object
        c = {
            "case_id": _alert["alert_id"],
            "organization_id": "tenant-1",
            "primary_entity": request.content,
            "primary_entity_type": request.type.lower(), # IMPORTANT! This maps to URL, SMS, EMAIL, QR
            "source_ip": request.type.upper(),
            "status": "OPEN",
            "severity": final_result["classification"],
            "risk_score": final_result.get("risk_score", 0.0),
            "title": f"Scan Investigation: {request.type.upper()}",
            "threat_summary": final_result["threat_type"],
            "alerts": [_alert],
            "first_seen": _alert["timestamp"],
            "last_seen": _alert["timestamp"],
            "created_at": _alert["timestamp"],
            "updated_at": _alert["timestamp"],
        }
        await mongo.upsert_case(c)
    except Exception as e:
        logger.error(f"Failed to persist scan case: {e}")
        
    return final_result
"""

content = content.replace("    return final_result", case_save_logic)

with open('backend/main.py', 'w') as f:
    f.write(content)

print("Updated backend/main.py")
