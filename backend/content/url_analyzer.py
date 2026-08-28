import math
import re
import os
import joblib
from typing import Dict, Tuple, List, Optional
from urllib.parse import urlparse
import hashlib
import numpy as np

# Load XGBoost model once
model_path = os.path.join(os.path.dirname(__file__), '../../models/url_xgb_v1.pkl')
try:
    xgb_model = joblib.load(model_path)
    MODEL_LOADED = True
except Exception as e:
    print(f"Warning: URL XGBoost model not found at {model_path}. Fallback to rules. {e}")
    MODEL_LOADED = False

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    from collections import Counter
    counts = Counter(s)
    total = len(s)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def extract_lexical_features(url: str, domain: str, path: str) -> Dict[str, float]:
    domain_len = len(domain)
    url_len = len(url)
    digits_domain = sum(c.isdigit() for c in domain)
    
    return {
        "lex_total_length": float(url_len),
        "lex_domain_length": float(domain_len),
        "lex_domain_entropy": shannon_entropy(domain),
        "lex_numeric_ratio": digits_domain / domain_len if domain_len > 0 else 0.0,
    }

def extract_structural_features(url: str, domain: str) -> Dict[str, float]:
    parts = domain.split('.')
    return {
        "struct_num_subdomains": float(len(parts) - 2 if len(parts) > 2 else 0),
        "struct_has_ip_in_domain": 1.0 if re.match(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', domain) else 0.0,
    }

def extract_domain_features(domain: str) -> Dict[str, float]:
    suspicious_tlds = {'.zip', '.mov', '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top'}
    has_suspicious_tld = any(domain.endswith(tld) for tld in suspicious_tlds)
    
    return {
        "domain_has_suspicious_tld": 1.0 if has_suspicious_tld else 0.0,
        "domain_has_hex_pattern": 1.0 if bool(re.search(r'[0-9a-f]{8,}', domain.lower())) else 0.0,
    }

def extract_behavioral_features(url: str) -> Dict[str, float]:
    brands = ['paypal', 'login', 'microsoft', 'apple', 'google', 'bank', 'hdfc', 'kyc', 'secure', 'account']
    brand_spoofing = any(brand in url.lower() for brand in brands)
    return {
        "behav_brand_spoofing": 1.0 if brand_spoofing else 0.0,
    }

def analyze_url(url: str) -> Tuple[float, str, Dict]:
    if not url:
        return 0.0, "Empty URL", {}
        
    try:
        if not url.startswith('http'):
            url = 'http://' + url
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
    except Exception:
        domain = ""
        path = ""
        
    features = {}
    features.update(extract_lexical_features(url, domain, path))
    features.update(extract_structural_features(url, domain))
    features.update(extract_domain_features(domain))
    features.update(extract_behavioral_features(url))
    
    if MODEL_LOADED:
        feature_vector = [
            features.get('lex_domain_entropy', 0.0),
            features.get('lex_total_length', 0.0),
            features.get('lex_numeric_ratio', 0.0),
            features.get('domain_has_hex_pattern', 0.0),
            features.get('struct_num_subdomains', 0.0),
            features.get('domain_has_suspicious_tld', 0.0),
            features.get('struct_has_ip_in_domain', 0.0),
            features.get('behav_brand_spoofing', 0.0)
        ]
        score = float(xgb_model.predict_proba([feature_vector])[0][1])
        reasons = []
        if features["lex_domain_entropy"] > 3.5: reasons.append("high_domain_entropy")
        if features["struct_has_ip_in_domain"] > 0: reasons.append("ip_in_domain")
        if features["behav_brand_spoofing"] > 0: reasons.append("brand_spoofing")
        if features["domain_has_suspicious_tld"] > 0: reasons.append("suspicious_tld")
        explanation = ", ".join(reasons) if reasons else "ML prediction based on URL features"
    else:
        score = 0.0
        reasons = []
        if features["lex_domain_entropy"] > 3.5: score += 0.3; reasons.append("high_domain_entropy")
        if features["lex_total_length"] > 75: score += 0.2; reasons.append("excessive_length")
        if features["domain_has_hex_pattern"] > 0: score += 0.3; reasons.append("hex_pattern")
        if features["struct_has_ip_in_domain"] > 0: score += 0.5; reasons.append("ip_in_domain")
        score = min(1.0, score)
        explanation = ", ".join(reasons) if reasons else "benign"
    
    return score, explanation, features
