import re
import sys

def patch_file():
    with open("backend/main.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add imports at the top
    imports = "from backend.auth import get_current_user, get_current_tenant, require_permissions, log_audit, db_client\nfrom fastapi import Depends\n"
    if "from backend.auth import get_current_user" not in content:
        content = imports + content

    # 2. Patch scan_content
    scan_orig = r"async def scan_content\(request: ScanRequest\):"
    scan_new = r"async def scan_content(request: ScanRequest, tenant_id: str = Depends(get_current_tenant), user: dict = Depends(get_current_user)):"
    content = re.sub(scan_orig, scan_new, content)
    
    case_orig = r"case = CyberCase\("
    case_new = r"case = CyberCase(\n        organization_id=tenant_id,"
    content = re.sub(case_orig, case_new, content)
    
    audit_patch = '''    try:
        await mongo.upsert_case(case_dump)
        log_audit(tenant_id, user.get("sub", "system"), "CREATE_SCAN", "CyberCase", str(case.case_id), {"type": request.type})
    except'''
    content = content.replace("    try:\n        await mongo.upsert_case(case_dump)\n    except", audit_patch)

    # 3. Patch get_cases
    cases_orig = r"async def get_cases\(\):\s+try:\s+cursor = mongo\.cases\.find\(\{.*?\}\)"
    cases_new = r"""async def get_cases(tenant_id: str = Depends(get_current_tenant)):
    try:
        cursor = mongo.cases.find({"organization_id": tenant_id})"""
    content = re.sub(cases_orig, cases_new, content)

    # 4. Patch get_case_by_id
    case_id_orig = r"async def get_case_by_id\(case_id: str\):"
    case_id_new = r"async def get_case_by_id(case_id: str, tenant_id: str = Depends(get_current_tenant)):"
    content = re.sub(case_id_orig, case_id_new, content)
    
    find_orig = r'db_case = await mongo\.cases\.find_one\(\{"case_id": case_id\}\)'
    find_new = r'db_case = await mongo.cases.find_one({"case_id": case_id, "organization_id": tenant_id})'
    content = re.sub(find_orig, find_new, content)
    
    in_mem_orig = r"if str\(c\.case_id\) == case_id:"
    in_mem_new = r"if str(c.case_id) == case_id and getattr(c, 'organization_id', 'default_org') == tenant_id:"
    content = re.sub(in_mem_orig, in_mem_new, content)

    # 5. Patch get_case_graph
    graph_orig = r"async def get_case_graph\(case_id: str\):"
    graph_new = r"async def get_case_graph(case_id: str, tenant_id: str = Depends(get_current_tenant)):"
    content = re.sub(graph_orig, graph_new, content)
    
    call_orig = r"case = await get_case_by_id\(case_id\)"
    call_new = r"case = await get_case_by_id(case_id, tenant_id)"
    content = re.sub(call_orig, call_new, content)
    
    # 6. Patch get_recent_alerts
    alerts_orig = r"async def get_recent_alerts\(limit: int = 100\):\s+try:\s+cursor = mongo\.alerts\.find\(\{.*?\}\)"
    alerts_new = r"""async def get_recent_alerts(limit: int = 100, tenant_id: str = Depends(get_current_tenant)):
    try:
        cursor = mongo.alerts.find({"organization_id": tenant_id})"""
    content = re.sub(alerts_orig, alerts_new, content)
    
    # 7. Patch get_stats
    stats_orig = r"async def get_stats\(\):"
    stats_new = r"async def get_stats(tenant_id: str = Depends(get_current_tenant)):"
    content = re.sub(stats_orig, stats_new, content)
    
    stats_c1 = r'active = await mongo\.cases\.count_documents\(\{"status": "OPEN"\}\)'
    stats_c1_new = r'active = await mongo.cases.count_documents({"status": "OPEN", "organization_id": tenant_id})'
    content = re.sub(stats_c1, stats_c1_new, content)
    
    stats_c2 = r'critical = await mongo\.cases\.count_documents\(\{"severity": \{"\": \["CRITICAL", "HIGH"\]\}\}\)'
    stats_c2_new = r'critical = await mongo.cases.count_documents({"severity": {"": ["CRITICAL", "HIGH"]}, "organization_id": tenant_id})'
    content = re.sub(stats_c2, stats_c2_new, content)

    # 8. Add Audit Logs endpoint
    if "@app.get(\"/api/audit\")" not in content:
        audit_endpoint = """
@app.get("/api/audit")
async def get_audit_logs_api(limit: int = 100, tenant_id: str = Depends(get_current_tenant), user: dict = Depends(get_current_user)):
    cursor = db_client.get_collection("audit_logs").find({"organization_id": tenant_id}).sort("created_at", -1).limit(limit)
    logs = []
    for log in cursor:
        if "_id" in log:
            log["_id"] = str(log["_id"])
        logs.append(log)
    return logs
"""
        content += audit_endpoint
        
    with open("backend/main.py", "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Surgically patched main.py for Tenant Context!")

if __name__ == "__main__":
    patch_file()
