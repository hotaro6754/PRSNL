import re

with open('frontend/src/app/ml/page.tsx', 'r') as f:
    code = f.read()

# Add the hooks inside ModelLab()
component_decl = r'(export default function ModelLab\(\) \{)'
hooks_to_insert = """
  const [prCurveData, setPrCurveData] = useState([]);
  const [featureImportance, setFeatureImportance] = useState([]);
"""
if "setPrCurveData" not in code:
    code = re.sub(component_decl, r'\1\n' + hooks_to_insert, code)

with open('frontend/src/app/ml/page.tsx', 'w') as f:
    f.write(code)
print("Inserted hooks into ModelLab")
