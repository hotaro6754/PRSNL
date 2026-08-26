import re
test_cases = [
    'Block1[Block (Known Malware)]',
    'BehaviorCheck{Behavioral Analysis Engine (Heuristics)}',
    'SIEM[(SIEM Engine)]',
    'A[conn.log (Connections)]',
    'AlreadyQuoted["Text (parens)"]'
]
for tc in test_cases:
    # 1. Fix unquoted square brackets with parens inside, avoiding databases [()]
    tc = re.sub(r'([A-Za-z0-9_]+)\[(?!\()([^\"\[\]]*\([^\[\]]+\)[^\"\[\]]*)(?<!\))\]', r'\1["\2"]', tc)
    # 2. Fix unquoted curly braces with parens inside
    tc = re.sub(r'([A-Za-z0-9_]+)\{([^\"\{\}]*\([^\{\}]+\)[^\"\{\}]*)\}', r'\1{"\2"}', tc)
    # 3. Fix unquoted databases
    tc = re.sub(r'([A-Za-z0-9_]+)\[\(([^\"()]+)\)\]', r'\1[("\2")]', tc)
    print(tc)
