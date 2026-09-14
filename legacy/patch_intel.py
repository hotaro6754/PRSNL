import sys

with open('backend/main.py', 'r') as f:
    code = f.read()

replacement = '''    evidence = []
    
    from backend.content.threat_intel import check_misp_urlhaus, check_playwright, check_agent_reach

    if isinstance(features, list):
        evidence = features
    else:
        for k, v in features.items():
            if v > 0:
                evidence.append(
                    DetectionEvidence(
                        feature=k,
                        value=v,
                        contribution=score if type(v) in (int, float) else 0.0,
                        explanation=f"{title_prefix} feature: {k}",
                        category=category,
                        source=source
                    )
                )
                
    # Add external integrations for demo purposes
    if request.type == "url" or request.type == "qr":
        intel_ev = check_misp_urlhaus(request.content, score) + check_playwright(request.content, score)
        for ie in intel_ev:
            evidence.append(
                DetectionEvidence(
                    feature=ie["evidence_type"],
                    value=1.0,
                    contribution=score,
                    explanation=str(ie["details"]),
                    category="threat_intel",
                    source="external_api"
                )
            )
            
    if request.type in ("sms", "email", "qr"):
        agent_ev = check_agent_reach(request.content, score)
        for ae in agent_ev:
            evidence.append(
                DetectionEvidence(
                    feature=ae["evidence_type"],
                    value=1.0,
                    contribution=score,
                    explanation=str(ae["details"]),
                    category="nlp_engine",
                    source="agent_reach"
                )
            )'''

code = code.replace('''    evidence = []
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
            )''', replacement)

with open('backend/main.py', 'w') as f:
    f.write(code)
