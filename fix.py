with open('parity_check.py', 'r') as f:
    lines = f.readlines()
with open('parity_check.py', 'w') as f:
    for line in lines:
        if 'def compare_all' in line:
            break
        f.write(line)
