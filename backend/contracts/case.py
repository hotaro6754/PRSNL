from pydantic import BaseModel
from typing import List, Literal, Optional, Any
from uuid import UUID
from datetime import datetime
from backend.contracts.alert import Alert

class SecurityCase(BaseModel):
    """
    Normalized Security Case schema.
    """
    case_id: UUID
    source_ip: str
    status: Literal["OPEN", "CLOSED"] = "OPEN"
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    risk_score: Optional[float] = None
    title: str = "Correlated Threat Detection"
    threat_summary: str
    alerts: List[Alert]
    evidence: Optional[List[Any]] = None
    first_seen: datetime
    last_seen: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    detection_sources: Optional[List[str]] = None
