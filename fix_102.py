lines = []
with open('backend/ml/registry.py', 'r') as f:
    for i, line in enumerate(f):
        if i == 101: # line index 101 is line 102
            lines.append('                    {"": update_fields},\n')
        else:
            lines.append(line)
with open('backend/ml/registry.py', 'w') as f:
    f.writelines(lines)
