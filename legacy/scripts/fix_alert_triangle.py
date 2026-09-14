import re

with open('frontend/src/app/ml/page.tsx', 'r') as f:
    code = f.read()

# Add AlertTriangle to lucide-react imports if it's missing
if 'AlertTriangle' not in code.split('\n')[1]: # Assuming imports are at the top
    code = re.sub(
        r'import \{ (.*?) \} from \'lucide-react\'',
        r'import { \1, AlertTriangle } from \'lucide-react\'',
        code
    )
else:
    # If there's no lucide-react import at all, add it
    if 'lucide-react' not in code:
        code = "import { AlertTriangle } from 'lucide-react';\n" + code

with open('frontend/src/app/ml/page.tsx', 'w') as f:
    f.write(code)
print("Fixed AlertTriangle import in ML page")
