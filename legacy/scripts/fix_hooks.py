import re

with open('frontend/src/app/ml/page.tsx', 'r') as f:
    code = f.read()

# Remove the broken top-level useState
code = re.sub(r'const \[prCurveData, setPrCurveData\] = useState\(\[\]\);\s*', '', code)
code = re.sub(r'const \[featureImportance, setFeatureImportance\] = useState\(\[\]\);\s*', '', code)

# We need to find the MLDashboard component declaration
# export default function MLDashboard() {
# and insert the hooks right after it.

component_decl = r'(export default function MLDashboard\(\) \{)'
hooks_to_insert = """
  const [prCurveData, setPrCurveData] = useState([]);
  const [featureImportance, setFeatureImportance] = useState([]);
"""

code = re.sub(component_decl, r'\1\n' + hooks_to_insert, code)

with open('frontend/src/app/ml/page.tsx', 'w') as f:
    f.write(code)
print("Fixed frontend ML page React hook placement")
