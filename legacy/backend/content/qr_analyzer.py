import re
from typing import Dict, Tuple, List
import hashlib
from backend.contracts.evidence import DetectionEvidence, Provenance
from backend.content.url_analyzer import analyze_url

def analyze_qr_code(content: str) -> Tuple[float, str, List[DetectionEvidence]]:
    if not content:
        return 0.0, "Empty QR", []

    text_hash = hashlib.sha256(content.encode()).hexdigest()
    
    prov = Provenance(
        source_event_id="qr-analysis",
        input_hash=text_hash,
        pipeline="qr-pipeline",
        model_id="qr_analyzer",
        model_version="1.0",
        feature_schema_version="1.0"
    )

    evidence_list = []
    
    # 1. Look for URLs inside the decoded QR content
    url_pattern = re.compile(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+')
    urls = url_pattern.findall(content)
    
    highest_url_risk = 0.0
    for url in urls:
        url_score, _, _ = analyze_url(url)
        if url_score > highest_url_risk:
            highest_url_risk = url_score
            
    if urls:
        evidence_list.append(DetectionEvidence(
            feature="qr_urls_found",
            value=urls,
            contribution=0.0,
            explanation="URLs embedded in QR Code",
            category="qr",
            crypto_provenance=prov,
            raw_input_hash=text_hash
        ))
        
        if highest_url_risk > 0:
            evidence_list.append(DetectionEvidence(
                feature="qr_url_risk",
                value=highest_url_risk,
                contribution=highest_url_risk,
                explanation="Malicious URL embedded in QR Code",
                category="qr",
                crypto_provenance=prov,
                raw_input_hash=text_hash
            ))
            
    # 2. Heuristics for non-URL payload
    is_vcard = "BEGIN:VCARD" in content
    is_wifi = "WIFI:" in content
    is_sms = "smsto:" in content.lower()
    
    if is_wifi:
        evidence_list.append(DetectionEvidence(
            feature="qr_wifi_payload",
            value=True,
            contribution=0.2,
            explanation="QR contains WiFi configuration (potential rogue AP)",
            category="qr",
            crypto_provenance=prov,
            raw_input_hash=text_hash
        ))
        
    score = 0.0
    reasons = []
    
    if highest_url_risk > 0:
        score += highest_url_risk
        reasons.append(f"quishing_url_risk_{highest_url_risk:.2f}")
        
    if is_wifi:
        score += 0.2
        reasons.append("wifi_rogue_ap_risk")
        
    score = min(1.0, score)
    explanation = ", ".join(reasons) if reasons else "benign_qr"
    
    return score, explanation, evidence_list
