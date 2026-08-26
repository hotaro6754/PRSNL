import glob
for fpath in ['backend/ml/resolver.py', 'backend/ml/registry.py', 'backend/ml/router.py']:
    with open(fpath, 'r') as f:
        content = f.read()
    content = content.replace('\\"', '"')
    with open(fpath, 'w') as f:
        f.write(content)
