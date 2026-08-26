import re
with open('backend/ml/registry.py', 'r') as f:
    c = f.read()
c = re.sub(r'\{\"\":', '{"":', c)
c = c.replace('{\\":', '{"":')
c = c.replace('{"": {"stage"', '{"": {"stage"')
# Let's just fix line 89 manually.
lines = c.split('\n')
for i, l in enumerate(lines):
    if 'ModelStage.SHADOW.value, "retired_at"' in l:
        lines[i] = '                            {"": {"stage": ModelStage.SHADOW.value, "retired_at": datetime.now(timezone.utc)}},'
    if 'update_fields}' in l and '{\\":' in l:
        lines[i] = '                    {"": update_fields},'
with open('backend/ml/registry.py', 'w') as f:
    f.write('\n'.join(lines))
