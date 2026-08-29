import os

def fix_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    if r'\"\"\"' in content:
        content = content.replace(r'\"\"\"', '\"\"\"')
        with open(path, 'w') as f:
            f.write(content)
        print(f"Fixed {path}")

for root, _, files in os.walk('backend'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))
