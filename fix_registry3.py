lines = []
with open('backend/ml/registry.py', 'r') as f:
    for line in f:
        if 'update_fields}' in line:
            lines.append('                    {"": update_fields},\n')
        else:
            lines.append(line)
with open('backend/ml/registry.py', 'w') as f:
    f.writelines(lines)
