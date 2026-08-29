from pydantic import BaseModel
from typing import List, Literal, Optional, Any
from uuid import UUID
from datetime import datetime
from backend.contracts.alert import Alert

class CyberCase(BaseModel):
    organization_id: str = "default_org"
    """
    Normalized Security Case schema.
    """
    case_id: UUID
    primary_entity: str
    source_ip: Optional[str] = None
    status: Literal["OPEN", "CLOSED", "ESCALATED", "RESOLVED", "FALSE_POSITIVE"] = "OPEN"
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
    primary_entity_type: Optional[str] = None
    related_entities: Optional[List[str]] = None
    attack_chain: Optional[List[str]] = None
