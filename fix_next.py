import re

with open('frontend/next.config.ts', 'r') as f:
    code = f.read()

# Replace or remove the eslint config
code = re.sub(r'eslint:\s*\{[^}]*\},\s*', '', code)

with open('frontend/next.config.ts', 'w') as f:
    f.write(code)
print('Fixed next.config.ts')
