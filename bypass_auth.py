import re

with open('backend/auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

mock_tenant = """
async def get_current_user(token: str = None):
    return {"sub": "admin@cyberos.local", "org_id": "tenant-1", "scopes": ["admin"]}

async def get_current_tenant(token: str = None):
    return "tenant-1"
"""

# We'll replace the existing get_current_user and get_current_tenant functions
content = re.sub(r'async def get_current_user.*?return payload', '', content, flags=re.DOTALL)
content = re.sub(r'async def get_current_tenant.*?return payload\.get\("org_id"\)', '', content, flags=re.DOTALL)

# Remove the oauth2_scheme dependency
content = content.replace('token: str = Depends(oauth2_scheme)', 'token: str = None')

content += "\n" + mock_tenant

with open('backend/auth.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Auth bypassed.")
