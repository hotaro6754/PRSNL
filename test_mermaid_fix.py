import re

def fix_block(block):
    lines = block.group(1).split('\n')
    out_lines = []
    for line in lines:
        def repl_square(m):
            node_id = m.group(1)
            content = m.group(2)
            if content.startswith('"') and content.endswith('"'):
                return m.group(0)
            if content.startswith('(') and content.endswith(')'):
                inner = content[1:-1]
                if '"' not in inner:
                    return f'{node_id}[("{inner}")]'
                return m.group(0)
            if '(' in content or ')' in content or '<' in content or ' ' in content:
                if '"' not in content:
                    return f'{node_id}["{content}"]'
            return m.group(0)
        
        line = re.sub(r'([A-Za-z0-9_]+)\[([^\]]+)\]', repl_square, line)
        
        def repl_curly(m):
            node_id = m.group(1)
            content = m.group(2)
            if content.startswith('"') and content.endswith('"'):
                return m.group(0)
            if '(' in content or ')' in content or '<' in content or ' ' in content:
                if '"' not in content:
                    return f'{node_id}{{"{content}"}}'
            return m.group(0)
            
        line = re.sub(r'([A-Za-z0-9_]+)\{([^}]+)\}', repl_curly, line)
        out_lines.append(line)
    return "`mermaid\n" + "\n".join(out_lines) + "`"

test_str = '''`mermaid
flowchart TD
    File[New File Executed]
    File --> SigCheck{Signature Check}
    SigCheck -->|Match found| Block1[Block (Known Malware)]
    SigCheck -->|No match| BehaviorCheck{Behavioral Analysis Engine}
    BehaviorCheck -->|Acts suspiciously| Block2[Block (Zero-Day Malware)]
    BehaviorCheck -->|Acts normal| Allow[Allow Execution]
    SIEM[(SIEM Engine)]
    A[conn.log (Connections)]
    AlreadyQuoted["Text (parens)"]
`'''

print(re.sub(r'`mermaid(.*?)`', fix_block, test_str, flags=re.DOTALL))
