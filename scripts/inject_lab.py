import re

with open('backend/main.py', 'r') as f:
    code = f.read()

lab_routes = """
from fastapi.responses import HTMLResponse

@app.get("/lab/benign", response_class=HTMLResponse)
async def lab_benign():
    return \"\"\"
    <html>
        <head><title>CyberOS Lab - Benign</title></head>
        <body>
            <h1>Benign Controlled Page</h1>
            <p>This is a purely static, benign page for testing web analysis without external variables.</p>
        </body>
    </html>
    \"\"\"

@app.get("/lab/login", response_class=HTMLResponse)
async def lab_login():
    return \"\"\"
    <html>
        <head><title>CyberOS Lab - Login</title></head>
        <body>
            <h1>Secure Portal</h1>
            <form action="/login" method="POST">
                <input type="text" name="username" placeholder="Username" />
                <input type="password" name="password" placeholder="Password" />
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    \"\"\"
"""

if "@app.get(\"/lab/benign\")" not in code:
    code = code.replace("app = FastAPI(", lab_routes + "\napp = FastAPI(")

with open('backend/main.py', 'w') as f:
    f.write(code)
print("Injected LAB controlled sites into main.py")
