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
        confidence = "LOW"
        threat_type = "unknown"
        
        # 1. Extract RAW signals (including dynamically mapped ones)
        ml_score = detection_results.get("ml_score", 0.0)
        
        # If URL analyzer populated it nested, pull it out
        if "url_analysis" in detection_results:
            ml_score = max(ml_score, detection_results["url_analysis"].get("score", 0.0))
            if ml_score > 0 and threat_type == "unknown":
                threat_type = "url_phishing"
                
        ml_threat = detection_results.get("ml_threat_type", threat_type)
        intel_score = detection_results.get("intel_score", 0.0)
        
        pattern_score = 0.0
        if patterns:
            pattern_score = max(p.get("severity", 0.0) for p in patterns)
            for p in patterns:
                evidence.append({
                    "source": "Pattern Matching",
                    "description": p["description"],
                    "severity": p["severity"]
                })
            if threat_type == "unknown" or threat_type == "url_phishing":
                threat_type = patterns[0].get("category", "suspicious")
                
        if ml_score > 0:
            evidence.append({
                "source": "ML Detection",
                "description": f"Model detected anomaly with score {ml_score:.2f}",
                "severity": ml_score
            })
            if threat_type == "unknown":
                threat_type = ml_threat

        if intel_score > 0:
            evidence.append({
                "source": "Threat Intel",
                "description": "Known malicious indicator matched",
                "severity": intel_score
            })
            
        # 2. Compute true combined risk using Probabilistic OR
        # This ensures that if ANY engine (like pattern) gives 0.85, the risk is at least 85!
        combined_prob = 1.0 - ((1.0 - ml_score) * (1.0 - pattern_score) * (1.0 - intel_score))
        
        risk_score = combined_prob * 100.0
        
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
