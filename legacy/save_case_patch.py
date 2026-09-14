import sys

with open('backend/main.py', 'r') as f:
    code = f.read()

replacement = '''    
    case_dump = case.model_dump(mode="json")
    try:
        await mongo.upsert_case(case_dump)
    except Exception as e:
        logger.error(f"Failed to save scan case to mongo: {e}")
        
    return case_dump'''

code = code.replace('    return case.model_dump(mode="json")', replacement)

with open('backend/main.py', 'w') as f:
    f.write(code)
