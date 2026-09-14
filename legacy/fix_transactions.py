import re

with open('backend/ml/registry.py', 'r') as f:
    content = f.read()

# Replace session.start_transaction() block with a normal execution
content = content.replace(\"\"\"        async with await self.client.start_session() as session:
            async with session.start_transaction():\"\"\", \"\"\"        session = None
        if True:\"\"\")

with open('backend/ml/registry.py', 'w') as f:
    f.write(content)
