import sys

with open('backend/main.py', 'r') as f:
    code = f.read()

replacement = '''    evidence = []
    if isinstance(features, list):
        evidence = features
    else:
        for k, v in features.items():
            evidence.append(
                DetectionEvidence(
                    feature=k,
                    value=v,
                    contribution=score if type(v) in (int, float) else 0.0,
                    explanation=f"{title_prefix} feature: {k}",
                    category=category,
                    source=source
                )
            )'''

code = code.replace('''    evidence = []
    for k, v in features.items():
        evidence.append(
            DetectionEvidence(
                feature=k,
                value=v,
                contribution=score if type(v) in (int, float) else 0.0,
                explanation=f"{title_prefix} feature: {k}",
                category=category,
                source=source
            )
        )''', replacement)

with open('backend/main.py', 'w') as f:
    f.write(code)
