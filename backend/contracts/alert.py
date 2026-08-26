from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from uuid import UUID
from datetime import datetime
from backend.contracts.evidence import DetectionEvidence

class Alert(BaseModel):
    """
    Normalized Alert schema for deterministic detections.
    """
    alert_id: UUID
    timestamp: datetime
    flow_id: str
    source_ip: str
    destination_ip: str
    protocol: str
    threat_class: str
    detector_id: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    confidence: float
    observability_score: float = Field(..., ge=0.0, le=1.0)
    evidence: List[DetectionEvidence]
    detector_version: str = "1.0"
    explanation: Optional[str] = None
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
