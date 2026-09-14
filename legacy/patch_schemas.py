import re

def patch_schema(filepath, class_name):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if organization_id already exists
    if "organization_id: str" in content:
        return
        
    orig = f"class {class_name}(BaseModel):"
    new = f"class {class_name}(BaseModel):\n    organization_id: str = \"default_org\""
    content = content.replace(orig, new)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
patch_schema("backend/contracts/case.py", "CyberCase")
patch_schema("backend/contracts/alert.py", "Alert")
patch_schema("backend/contracts/evidence.py", "DetectionEvidence")
print("Schemas patched.")
