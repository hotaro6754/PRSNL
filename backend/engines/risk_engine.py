from typing import Dict, Any, List

class RiskEngine:
    def __init__(self):
        # Weights for different signal sources
        self.weights = {
            "ml_model": 0.4,
            "patterns": 0.3,
            "threat_intel": 0.3
        }

    def evaluate(self, input_type: str, detection_results: Dict[str, Any], patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        evidence = []
        total_risk = 0.0
        confidence = "LOW"
        threat_type = "unknown"
        
        # ML Model Signal
        ml_score = detection_results.get("ml_score", 0.0)
        ml_threat = detection_results.get("ml_threat_type", "unknown")
        
        if ml_score > 0:
            evidence.append({
                "source": "ML Detection",
                "description": f"Model detected potential {ml_threat} with score {ml_score:.2f}",
                "severity": ml_score
            })
            total_risk += ml_score * self.weights["ml_model"]
            threat_type = ml_threat
            
        # Pattern Signal
        pattern_score = 0.0
        if patterns:
            max_pattern_severity = max(p.get("severity", 0.0) for p in patterns)
            pattern_score = max_pattern_severity
            for p in patterns:
                evidence.append({
                    "source": "Pattern Matching",
                    "description": p["description"],
                    "severity": p["severity"]
                })
            total_risk += pattern_score * self.weights["patterns"]
            if threat_type == "unknown" and patterns:
                threat_type = patterns[0].get("category", "suspicious")
                
        # Threat Intel Signal (mock)
        intel_score = detection_results.get("intel_score", 0.0)
        if intel_score > 0:
            evidence.append({
                "source": "Threat Intel",
                "description": "Known malicious indicator matched",
                "severity": intel_score
            })
            total_risk += intel_score * self.weights["threat_intel"]
            
        # Normalize and Classify
        risk_score = min(total_risk * 100, 100.0)
        
        if risk_score > 85:
            classification = "CRITICAL"
            confidence = "HIGH"
        elif risk_score > 60:
            classification = "HIGH"
            confidence = "HIGH"
        elif risk_score > 35:
            classification = "MEDIUM"
            confidence = "MEDIUM"
        elif risk_score > 10:
            classification = "LOW"
            confidence = "MEDIUM"
        else:
            classification = "SAFE"
            confidence = "HIGH"
            
        if not evidence:
            classification = "UNVERIFIED"
            confidence = "LOW"
            
        return {
            "classification": classification,
            "risk_score": round(risk_score, 1),
            "threat_type": threat_type.upper(),
            "confidence": confidence,
            "evidence": evidence
        }
