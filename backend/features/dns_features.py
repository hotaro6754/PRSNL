import math
import re
from typing import Tuple, Dict

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

def dns_query_features(query_name: str) -> Dict:
    if not query_name:
        return {}
        
    query_name = query_name.rstrip('.')
    labels = query_name.split('.')
    
    if len(labels) > 1:
        sld = labels[-2]
    else:
        sld = labels[0]
        
    sld_len = len(sld)
    digits = sum(c.isdigit() for c in sld)
    consonants = sum(1 for c in sld.lower() if c.isalpha() and c not in 'aeiou')
    
    return {
        "domain": query_name,
        "sld": sld,
        "label_count": len(labels),
        "total_length": len(query_name),
        "sld_length": sld_len,
        "sld_entropy": shannon_entropy(sld),
        "numeric_ratio": digits / sld_len if sld_len > 0 else 0,
        "consonant_ratio": consonants / sld_len if sld_len > 0 else 0,
        "has_hex_pattern": bool(re.search(r'[0-9a-f]{8,}', sld.lower())),
        "max_label_length": max((len(l) for l in labels), default=0)
    }

def is_suspicious_dns(features: Dict) -> Tuple[bool, float, str]:
    if not features:
        return False, 0.0, ""
        
    sld_entropy = features.get("sld_entropy", 0.0)
    total_length = features.get("total_length", 0)
    numeric_ratio = features.get("numeric_ratio", 0.0)
    has_hex = features.get("has_hex_pattern", False)
    
    if sld_entropy > 3.5:
        return True, min(0.95, sld_entropy / 5.0), "high_entropy"
    if total_length > 50:
        return True, min(0.9, total_length / 100.0), "excessive_length"
    if numeric_ratio > 0.4:
        return True, numeric_ratio, "high_numeric_ratio"
    if has_hex:
        return True, 0.8, "hex_pattern"
        
    return False, 0.0, ""
