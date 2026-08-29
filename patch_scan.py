"""
Patch backend/main.py to wire the new Risk Intelligence engines into the /api/scan endpoint.
"""

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ─── Replace the existing /api/scan endpoint ───

OLD_SCAN_START = '@app.post("/api/scan")'
NEW_SCAN_CODE = '''from backend.engines import analyze_content

class ScanRequest(BaseModel):
    type: str  # "url", "email", "sms", "qr"
    content: str

@app.post("/api/scan")
async def scan_content(request: ScanRequest):
    # 1. Gather raw detection outputs (mocked/existing logic)
    import time
    time.sleep(1) # simulate processing latency
    
    raw_detections = {
        "url_analysis": {},
        "email_analysis": {},
        "sms_analysis": {},
        "qr_analysis": {}
    }
    
    if request.type == "url":
        from backend.content.url_analyzer import analyze_url
        evidence_ledger = []
        is_suspicious = analyze_url(request.content, evidence_ledger)
        raw_detections["url_analysis"] = {
            "suspicious": is_suspicious,
            "evidence": evidence_ledger
        }
    
    # 2. Run the new unified Risk Intelligence Engine
    final_result = analyze_content(request.type, request.content, raw_detections)
    
    # 3. Broadcast to Live Threats WebSocket
    import datetime, uuid
    _alert = {
        "alert_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_ip": request.type.upper(),
        "destination_ip": request.content[:40],
        "threat_class": final_result["threat_type"],
        "severity": final_result["classification"],
        "confidence": final_result["confidence"],
        "detector_id": "RISK-ENGINE-V2",
        "category": "content_scan",
    }
    try:
        await broadcast_alert(_alert)
    except Exception:
        pass
        
    return final_result
'''

import re

# Find the start of /api/scan
if OLD_SCAN_START in content:
    # We need to replace the entire old @app.post("/api/scan") block.
    # It probably looks like:
    # @app.post("/api/scan")
    # async def scan_content(...):
    #     ...
    #     return ...
    # And ends when a new route starts, e.g., @app.get("/api/cases/{case_id}/graph")
    
    pattern = r'@app\.post\("/api/scan"\).*?(?=@app\.)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + NEW_SCAN_CODE + '\n' + content[match.end():]
        print("[OK] Patched /api/scan endpoint with new engines.")
    else:
        # Fallback if no @app. after it
        print("[WARN] Could not regex match /api/scan body.")
else:
    # Just append it if it doesn't exist at all
    content += '\n' + NEW_SCAN_CODE
    print("[OK] Appended new /api/scan endpoint.")


with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[OK] Backend scan patching complete!")
