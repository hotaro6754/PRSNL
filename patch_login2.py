import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_route = """
from pydantic import BaseModel
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/login")
async def api_auth_login(req: LoginRequest):
    if req.email == "admin@cyberos.local" and req.password == "admin":
        from backend.auth import create_access_token
        token = create_access_token({"sub": req.email, "org_id": "tenant-1", "scopes": ["admin"]})
        return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")
"""

content = content.replace('app = FastAPI(title="SIH 26145 - Passive NDR Backend")', 'app = FastAPI(title="SIH 26145 - Passive NDR Backend")\n' + new_route)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Injected login route!")
