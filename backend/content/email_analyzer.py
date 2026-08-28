import re
import email
import hashlib
from email import policy
from email.message import Message
from typing import Dict, Tuple, Any, List

from backend.content.url_analyzer import analyze_url
from backend.contracts.evidence import DetectionEvidence, Provenance

URGENCY_KEYWORDS = [
    'urgent', 'immediate', 'action required', 'account suspended',
    'verify now', 'warning', 'password reset', 'invoice', 'payment required',
    'security alert', 'unauthorized access'
]

def analyze_email(raw_content: str) -> Tuple[float, str, List[DetectionEvidence]]:
    if not raw_content:
        return 0.0, "Empty email", []

    if isinstance(raw_content, dict):
        raw_content = str(raw_content)

    email_hash = hashlib.sha256(raw_content.encode()).hexdigest()
    
    prov = Provenance(
        source_event_id="email-analysis",
        input_hash=email_hash,
        pipeline="email-pipeline",
        model_id="email_analyzer",
        model_version="1.0",
        feature_schema_version="1.0"
    )

    msg = email.message_from_string(raw_content, policy=policy.default)
    
    evidence_list = []
    
    # 1. Header Analysis (Mocked SPF/DKIM/DMARC)
    auth_results = msg.get("Authentication-Results", "").lower()
    spf_pass = "spf=pass" in auth_results
    dkim_pass = "dkim=pass" in auth_results
    dmarc_pass = "dmarc=pass" in auth_results
    
    evidence_list.append(DetectionEvidence(
        feature="auth_results",
        value={"spf_pass": spf_pass, "dkim_pass": dkim_pass, "dmarc_pass": dmarc_pass},
        contribution=0.3 if not spf_pass and not dkim_pass else 0.0,
        explanation="Email Authentication Results",
        category="email_header",
        crypto_provenance=prov,
        raw_input_hash=email_hash
    ))

    # 2. Sender Domain Mismatch
    from_header = msg.get("From", "")
    return_path = msg.get("Return-Path", "")
    
    def extract_domain(addr):
        match = re.search(r'@([\w.-]+)', addr)
        return match.group(1).lower() if match else ""
        
    from_domain = extract_domain(from_header)
    return_domain = extract_domain(return_path)
    domain_mismatch = bool(from_domain and return_domain and from_domain != return_domain)
    
    if domain_mismatch:
        evidence_list.append(DetectionEvidence(
            feature="domain_mismatch",
            value=True,
            contribution=0.4,
            explanation="Sender Domain Mismatch detected",
            category="email_header",
            crypto_provenance=prov,
            raw_input_hash=email_hash
        ))

    # 3. Urgency keywords in body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode(errors="ignore")
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        except:
            body = str(msg.get_payload())

    body_lower = body.lower()
    urgency_count = sum(1 for kw in URGENCY_KEYWORDS if kw in body_lower)
    urgency_score = min(1.0, urgency_count * 0.2)
    
    if urgency_score > 0:
        evidence_list.append(DetectionEvidence(
            feature="urgency_score",
            value=urgency_score,
            contribution=urgency_score * 0.4,
            explanation="Urgency keywords detected in email body",
            category="email_body",
            crypto_provenance=prov,
            raw_input_hash=email_hash
        ))

    # 4. Extract URLs
    url_pattern = re.compile(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+')
    urls = url_pattern.findall(body)
    
    highest_url_risk = 0.0
    for url in urls:
        url_score, _, _ = analyze_url(url)
        if url_score > highest_url_risk:
            highest_url_risk = url_score
            
    if highest_url_risk > 0:
        evidence_list.append(DetectionEvidence(
            feature="url_highest_risk",
            value=highest_url_risk,
            contribution=highest_url_risk * 0.6,
            explanation="Malicious URL risk in email body",
            category="email_body",
            crypto_provenance=prov,
            raw_input_hash=email_hash
        ))

    # Calculate final score
    score = 0.0
    reasons = []

    if not spf_pass and not dkim_pass:
        score += 0.3
        reasons.append("failed_auth")
        
    if domain_mismatch:
        score += 0.4
        reasons.append("domain_mismatch")
        
    if urgency_score > 0:
        score += urgency_score * 0.4
        reasons.append("urgency_keywords")
        
    if highest_url_risk > 0:
        score += highest_url_risk * 0.6
        reasons.append(f"malicious_url_risk_{highest_url_risk:.2f}")

    score = min(1.0, score)
    explanation = ", ".join(reasons) if reasons else "benign"
    
    return score, explanation, evidence_list
