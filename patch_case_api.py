"""
Patch backend/main.py to inject Explanation layers into /api/cases/{case_id}
"""
import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Locate the get_case_by_id function
# Replace it entirely

old_func_pattern = r'@app\.get\("/api/cases/\{case_id\}"\).*?raise HTTPException\(status_code=404, detail="Case not found"\)'

new_func = """@app.get("/api/cases/{case_id}")
async def get_case_by_id(case_id: str, tenant_id: str = Depends(get_current_tenant)):
    case = None
    cases = correlation_engine.get_all_cases()
    for c in cases:
        if str(c.case_id) == case_id and getattr(c, 'organization_id', 'default_org') == tenant_id:
            case = c.model_dump() if hasattr(c, 'model_dump') else c
            break
            
    if not case:
        try:
            from bson import ObjectId
            db_case = await mongo.cases.find_one({"case_id": case_id, "organization_id": tenant_id})
            if db_case:
                if "_id" in db_case:
                    del db_case["_id"]
                case = db_case
        except Exception:
            pass

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Ensure 5-layer explanation is attached to the case object for the frontend
    if "explanation" not in case or not case["explanation"]:
        from backend.engines import analyze_content
        # We can dynamically construct an explanation from the threat_summary and alerts
        case["explanation"] = {
            "what": f"The case has been classified as {case.get('severity', 'UNKNOWN')}.",
            "why": case.get('threat_summary', 'Correlated threat detected across multiple alerts.'),
            "evidence_summary": [a.get('threat_class', 'Alert') for a in case.get('alerts', [])][:5],
            "confidence": "System confidence is HIGH." if case.get('severity') in ['CRITICAL', 'HIGH'] else "System confidence is MEDIUM.",
            "action": "Investigate correlated alerts. Isolate affected host if critical.",
            "uncertainty": None
        }
        
    return case"""

content = re.sub(old_func_pattern, new_func, content, flags=re.DOTALL)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched /api/cases/{case_id}")
