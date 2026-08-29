import json
import os
import re
from typing import List, Dict, Any

class PatternEngine:
    def __init__(self):
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, Any]:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "threat_patterns.json")
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def analyze(self, input_type: str, content: str) -> List[Dict[str, Any]]:
        results = []
        if input_type not in self.patterns:
            return results
            
        rules = self.patterns[input_type]
        for rule in rules:
            try:
                if re.search(rule["regex"], content, re.IGNORECASE):
                    results.append({
                        "name": rule["name"],
                        "description": rule["description"],
                        "category": rule["category"],
                        "severity": rule["severity"]
                    })
            except re.error:
                continue
                
        return results
