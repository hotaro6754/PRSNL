import re

with open('frontend/src/app/ml/page.tsx', 'r') as f:
    code = f.read()

# Replace hardcoded data
code = re.sub(
    r'const prCurveData = \[.*?\];',
    'const [prCurveData, setPrCurveData] = useState([]);',
    code, flags=re.DOTALL
)

code = re.sub(
    r'const featureImportance = \[.*?\];',
    'const [featureImportance, setFeatureImportance] = useState([]);',
    code, flags=re.DOTALL
)

# Add useEffect to fetch data
fetch_effect = """
  React.useEffect(() => {
    fetch('http://localhost:8000/api/ml/metrics')
      .then(res => res.json())
      .then(data => {
        if (data.pr_curve) setPrCurveData(data.pr_curve);
        if (data.feature_importance) setFeatureImportance(data.feature_importance);
      })
      .catch(err => console.error("Failed to fetch ML metrics", err));
  }, []);
"""
code = code.replace('const [activeTab, setActiveTab] = useState(\'url\')', 'const [activeTab, setActiveTab] = useState(\'url\')\n' + fetch_effect)

with open('frontend/src/app/ml/page.tsx', 'w') as f:
    f.write(code)
print("Updated frontend to use real ML metrics")
