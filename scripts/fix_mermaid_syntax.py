import os
import re

d = r'E:\sih26145-prototype\educational_dashboard\raw_modules'

def fix_block(block_match):
    lines = block_match.group(1).split('\n')
    out_lines = []
    for line in lines:
        # Regex 1: Fix unquoted square brackets (including databases)
        def repl_square(m):
            node_id = m.group(1)
            content = m.group(2)
            
            # Already quoted? Skip.
            if content.startswith('"') and content.endswith('"'):
                return m.group(0)
            
            # Database shape [(...)]
            if content.startswith('(') and content.endswith(')'):
                inner = content[1:-1]
                if '"' not in inner:
                    return f'{node_id}[("{inner}")]'
                return m.group(0)
            
            # Subroutine shape [[...]]
            if content.startswith('[') and content.endswith(']'):
                inner = content[1:-1]
                if '"' not in inner:
                    return f'{node_id}[["{inner}"]]'
                return m.group(0)
            
            # Normal bracket but contains spaces or special characters
            if '(' in content or ')' in content or '<' in content or ' ' in content or '-' in content:
                if '"' not in content:
                    return f'{node_id}["{content}"]'
            return m.group(0)
        
        line = re.sub(r'([A-Za-z0-9_]+)\[([^\]]+)\]', repl_square, line)
        
        # Regex 2: Fix unquoted curly braces
        def repl_curly(m):
            node_id = m.group(1)
            content = m.group(2)
            
            if content.startswith('"') and content.endswith('"'):
                return m.group(0)
                
            if '(' in content or ')' in content or '<' in content or ' ' in content or '-' in content:
                if '"' not in content:
                    return f'{node_id}{{"{content}"}}'
            return m.group(0)
            
        line = re.sub(r'([A-Za-z0-9_]+)\{([^}]+)\}', repl_curly, line)
        out_lines.append(line)
        
    return "```mermaid\n" + "\n".join(out_lines) + "```"

if __name__ == "__main__":
    if not os.path.exists(d):
        print("Raw modules directory not found!")
        exit(1)
        
    files = [f for f in os.listdir(d) if f.endswith('.md')]
    fixed_count = 0
    
    for f in files:
        path = os.path.join(d, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        new_content = re.sub(r'```mermaid(.*?)```', fix_block, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Fixed mermaid syntax in {f}")
            fixed_count += 1
            
    print(f"Done. Fixed {fixed_count} files.")
