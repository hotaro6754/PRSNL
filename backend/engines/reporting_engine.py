import datetime
from typing import Dict, Any

class ReportingEngine:
    def generate_report_metadata(self, case_id: str, threat_type: str, classification: str) -> Dict[str, Any]:
        return {
            "report_id": f"REP-{case_id}",
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "threat_category": threat_type,
            "severity_level": classification,
            "status": "DRAFT"
        }
