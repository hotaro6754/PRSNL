import re
with open("backend/contracts/observation.py", "r", encoding="utf-8") as f:
    content = f.read()

orig = "class NetworkObservation(BaseModel):"
new = "class NetworkObservation(BaseModel):\n    organization_id: str = \"default_org\""
if "organization_id: str" not in content:
    content = content.replace(orig, new)

with open("backend/contracts/observation.py", "w", encoding="utf-8") as f:
    f.write(content)
