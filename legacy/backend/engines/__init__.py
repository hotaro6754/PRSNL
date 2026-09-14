from .risk_engine import RiskEngine
from .pattern_engine import PatternEngine
from .explanation_engine import ExplanationEngine
from .recommendation_engine import RecommendationEngine
from .reporting_engine import ReportingEngine
from .awareness_engine import AwarenessEngine

__all__ = [
    "RiskEngine",
    "PatternEngine",
    "ExplanationEngine",
    "RecommendationEngine",
    "ReportingEngine",
    "AwarenessEngine",
    "analyze_content",
]

# Confidence string -> float mapping
_CONF_MAP = {"HIGH": 0.92, "MEDIUM": 0.65, "LOW": 0.35}

def analyze_content(input_type: str, content: str, detection_results: dict) -> dict:
    import uuid

    case_id = f"CYB-{uuid.uuid4().hex[:8].upper()}"

    # 1. Detect patterns
    pattern_engine = PatternEngine()
    patterns = pattern_engine.analyze(input_type, content)

    # 2. Risk scoring
    risk_engine = RiskEngine()
    risk_result = risk_engine.evaluate(input_type, detection_results, patterns)

    classification = risk_result["classification"]
    risk_score = risk_result["risk_score"]
    raw_evidence = risk_result["evidence"]
    threat_type = risk_result["threat_type"]
    confidence_str = risk_result["confidence"]
    confidence = _CONF_MAP.get(confidence_str, 0.5)

    # 3. Generate explanation (flatten to frontend-expected keys)
    explanation_engine = ExplanationEngine()
    raw_expl = explanation_engine.generate(classification, threat_type, raw_evidence, confidence_str)
    explanation = {
        "what": raw_expl.get("WHAT", ""),
        "why": raw_expl.get("WHY", ""),
        "evidence_summary": [e["description"] for e in raw_evidence] if raw_evidence else ["No concrete evidence found."],
        "confidence": raw_expl.get("CONFIDENCE", ""),
        "uncertainty": raw_expl.get("UNCERTAINTY") if confidence_str != "HIGH" else None,
    }

    # 4. Get recommendations
    recommendation_engine = RecommendationEngine()
    recommendations = recommendation_engine.get_recommendations(threat_type, classification, input_type)

    # 5. Get awareness module
    awareness_engine = AwarenessEngine()
    raw_edu = awareness_engine.get_module_for_threat(threat_type)
    education = None
    if raw_edu:
        quiz_data = raw_edu.get("quiz", {})
        education = {
            "module_id": f"MOD-{threat_type[:8]}",
            "title": raw_edu.get("title", "Security Awareness"),
            "why_it_works": raw_edu.get("why_it_works", raw_edu.get("content", "")),
            "how_to_spot": raw_edu.get("how_to_spot", ["Check the sender", "Look for urgency", "Verify links"]),
            "quiz": {
                "question": quiz_data.get("question", ""),
                "options": quiz_data.get("options", []),
                "correct_answer": quiz_data.get("answer", quiz_data.get("correct_answer", 0)),
                "explanation": quiz_data.get("explanation", "Always verify before acting on suspicious content."),
            },
        }

    # 6. Generate report metadata
    reporting_engine = ReportingEngine()
    report_metadata = reporting_engine.generate_report_metadata(case_id, threat_type, classification)

    # 7. Evidence with provenance IDs
    evidence_provenance = []
    for i, ev in enumerate(raw_evidence):
        evidence_provenance.append({
            "evidence_id": f"EV-{case_id}-{i+1:03d}",
            "source": ev.get("source", "UNKNOWN"),
            "observation": ev.get("description", ""),
        })

    decision_summary = f"{threat_type} activity detected." if classification not in ("SAFE", "UNVERIFIED") else "No significant threats detected in the provided content."

    return {
        "case_id": case_id,
        "classification": classification,
        "risk_score": risk_score,
        "confidence": confidence,
        "threat_type": threat_type,
        "decision_summary": decision_summary,
        "suspicious_patterns": patterns,
        "evidence": evidence_provenance,
        "explanation": explanation,
        "recommendations": recommendations,
        "report_metadata": report_metadata,
        "education": education,
    }
