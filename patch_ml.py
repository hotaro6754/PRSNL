"""
Patch ml/page.tsx to fetch data from /api/ml/metrics
"""
import re

with open('frontend/src/app/(dashboard)/ml/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure we import useEffect
if "useEffect" not in content:
    content = content.replace("import React, { useState } from 'react'", "import React, { useState, useEffect } from 'react'")

# Add the fetch logic inside the ModelLab component
fetch_logic = """
  const [prCurveData, setPrCurveData] = useState([]);
  const [featureImportance, setFeatureImportance] = useState([]);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/ml/metrics')
      .then(res => res.json())
      .then(data => {
        if (data.pr_curve) {
          setPrCurveData(data.pr_curve);
        }
        if (data.feature_importance) {
          // Normalize the SHAP values slightly for UI or just use raw
          // Max value based scaling for the UI domain [0, 1] requires us to normalize them
          const maxVal = Math.max(...data.feature_importance.map((f: any) => f.value));
          const normalized = data.feature_importance.map((f: any) => ({
            name: f.name,
            value: maxVal > 0 ? f.value / maxVal : f.value,
            rawValue: f.value
          }));
          setFeatureImportance(normalized);
        }
        setMetrics(data);
      })
      .catch(console.error);
  }, []);
"""

content = re.sub(
    r"const \[prCurveData, setPrCurveData\] = useState\(\[\]\);\s*const \[featureImportance, setFeatureImportance\] = useState\(\[\]\);",
    fetch_logic.strip(),
    content
)

# Update the XAxis of the feature importance chart since we normalize to 1
if '<XAxis type="number" domain={[0, 1]}' not in content:
    content = content.replace('<XAxis type="number"', '<XAxis type="number" domain={[0, 1]}')

with open('frontend/src/app/(dashboard)/ml/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched ml/page.tsx")
