import json
import os
from typing import Dict, Any

class AwarenessEngine:
    def __init__(self):
        self.modules = self._load_modules()
        
    def _load_modules(self) -> Dict[str, Any]:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "awareness_modules.json")
        try:
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("modules", {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def get_module_for_threat(self, threat_type: str) -> Dict[str, Any]:
        threat_key = threat_type.lower()
        if threat_key in self.modules:
            return self.modules[threat_key]
        return self.modules.get("general_security", {})
