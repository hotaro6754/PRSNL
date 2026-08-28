import re
with open('backend/main.py', 'r') as f:
    code = f.read()

code = code.replace(
    'intel_ev = check_misp_urlhaus(request.content, score) + check_playwright(request.content, score)',
    'intel_ev = await check_misp_urlhaus(request.content, score)\n        intel_ev += await check_playwright(request.content, score)'
)
code = code.replace(
    'intel_ev = check_agent_reach(request.content, score)',
    'intel_ev = await check_agent_reach(request.content, score)'
)

with open('backend/main.py', 'w') as f:
    f.write(code)
print('Updated main.py to await async threat intel functions')
