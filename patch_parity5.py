import re

with open('parity_check.py', 'r') as f:
    content = f.read()

content = content.replace("                except Exception as e:\n                    pass", "                except Exception as e:\n                    import traceback\n                    traceback.print_exc()")

with open('parity_check.py', 'w') as f:
    f.write(content)
