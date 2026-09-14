import re
import os
import joblib
from typing import Dict, Tuple, Any, List
import hashlib
from backend.contracts.evidence import DetectionEvidence, Provenance
from backend.content.url_analyzer import analyze_url
import numpy as np

# Load XGBoost model once
model_path = os.path.join(os.path.dirname(__file__), '../../models/sms_xgb_v1.pkl')
try:
    sms_model = joblib.load(model_path)
    MODEL_LOADED = True
except Exception as e:
    print(f"Warning: SMS XGBoost model not found at {model_path}. Fallback to rules. {e}")
    MODEL_LOADED = False

SCAM_KEYWORDS = [
    'account suspended', 'verify now', 'action required', 'urgent',
    'win', 'prize', 'lottery', 'click here', 'login', 'password',
    'unauthorized', 'frozen', 'compromised', 'claim'
]

def analyze_sms(text: str) -> Tuple[float, str, List[DetectionEvidence]]:
    if not text:
        return 0.0, "Empty SMS", []

    text_hash = hashlib.sha256(text.encode()).hexdigest()
    
    prov = Provenance(
        source_event_id="sms-analysis",
        input_hash=text_hash,
        pipeline="sms-pipeline",
        model_id="sms_analyzer_xgb" if MODEL_LOADED else "sms_analyzer_rules",
        model_version="1.0",
        feature_schema_version="1.0"
    )

    evidence_list = []
    text_lower = text.lower()
    
    # Extract Features
    sms_length = len(text)
    
    url_pattern = re.compile(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+')
    urls = url_pattern.findall(text)
    sms_num_urls = len(urls)
    
    sms_scam_keyword_count = sum(1 for kw in SCAM_KEYWORDS if kw in text_lower)
    sms_urgency_score = min(1.0, sms_scam_keyword_count * 0.25)
    
    highest_url_risk = 0.0
    for url in urls:
        url_score, _, _ = analyze_url(url)
        if url_score > highest_url_risk:
            highest_url_risk = url_score
            
    # Record evidence
    if sms_scam_keyword_count > 0:
        evidence_list.append(DetectionEvidence(
            feature="scam_score", value=sms_urgency_score, contribution=0.5,
            explanation=f"{sms_scam_keyword_count} scam keywords detected", category="sms", crypto_provenance=prov, raw_input_hash=text_hash
        ))
    if urls:
        evidence_list.append(DetectionEvidence(
            feature="urls_found", value=urls, contribution=0.0,
            explanation=f"{sms_num_urls} URLs extracted from SMS", category="sms", crypto_provenance=prov, raw_input_hash=text_hash
        ))
    if highest_url_risk > 0:
        evidence_list.append(DetectionEvidence(
            feature="url_highest_risk", value=highest_url_risk, contribution=0.7,
            explanation=f"Malicious URL risk {highest_url_risk:.2f} in SMS", category="sms", crypto_provenance=prov, raw_input_hash=text_hash
        ))

    # Inference
    reasons = []
    if MODEL_LOADED:
        feature_vector = [
            float(sms_length),
            float(sms_num_urls),
            float(sms_scam_keyword_count),
            float(sms_urgency_score),
            float(highest_url_risk)
        ]
        score = float(sms_model.predict_proba([feature_vector])[0][1])
        if sms_scam_keyword_count > 0: reasons.append("scam_keywords")
        if highest_url_risk > 0.5: reasons.append("malicious_url_linked")
        explanation = ", ".join(reasons) if reasons else "ML prediction based on SMS features"
    else:
        score = 0.0
        if sms_urgency_score > 0: score += sms_urgency_score * 0.5; reasons.append("scam_keywords")
        if highest_url_risk > 0: score += highest_url_risk * 0.7; reasons.append(f"malicious_url_risk")
        score = min(1.0, score)
        explanation = ", ".join(reasons) if reasons else "benign"
    
    return score, explanation, evidence_list
