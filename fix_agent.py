import re
with open('backend/main.py', 'r') as f:
    code = f.read()
code = code.replace(
    'agent_ev = check_agent_reach(request.content, score)',
    'agent_ev = await check_agent_reach(request.content, score)'
)
with open('backend/main.py', 'w') as f:
    f.write(code)
print('Fixed agent_ev')
