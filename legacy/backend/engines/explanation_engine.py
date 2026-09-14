from typing import Dict, Any, List

class ExplanationEngine:
    def generate(self, classification: str, threat_type: str, evidence: List[Dict[str, Any]], confidence: str) -> Dict[str, str]:
        what = f"The content has been classified as {classification}."
        
        why = f"This classification is based on indicators pointing to a {threat_type} threat."
        if classification in ["SAFE", "UNVERIFIED"]:
             why = "No significant malicious indicators were found."
             
        evidence_summary = "Evidence includes: " + ", ".join(e["description"] for e in evidence[:3])
        if not evidence:
            evidence_summary = "No concrete evidence found."
            
        action = f"Based on this {classification} classification, please refer to the recommendations provided."
        
        uncertainty = "Analysis is highly certain." if confidence == "HIGH" else "Analysis may lack complete certainty due to limited data."
        
        return {
            "WHAT": what,
            "WHY": why,
            "EVIDENCE": evidence_summary,
            "CONFIDENCE": f"System confidence is {confidence}.",
            "ACTION": action,
            "UNCERTAINTY": uncertainty
        }
