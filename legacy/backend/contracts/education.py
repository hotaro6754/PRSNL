from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ThreatKnowledge(BaseModel):
    id: str
    title: str
    description: str
    severity: str = "medium"
    authoritative_sources: List[str] = Field(default_factory=list) # e.g., "CERT-In", "CISA", "OWASP"
    mitigation_steps: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LearningModule(BaseModel):
    id: str
    threat_knowledge_id: str
    title: str
    content: str # Quarkdown content
    quiz_questions: List[Dict[str, str]] = Field(default_factory=list)
    target_audience: str = "general"

class AwarenessReport(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    telemetry_summary: Dict[str, int] = Field(default_factory=dict)
    key_threats: List[ThreatKnowledge] = Field(default_factory=list)
    quarkdown_report: str
    
class StartupPostureReport(BaseModel):
    id: str
    startup_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vulnerabilities_detected: int = 0
    incidents_prevented: int = 0
    recommendations: List[str] = Field(default_factory=list)
    quarkdown_report: str

class SocietalImpactReport(BaseModel):
    id: str
    region: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    citizens_protected: int = 0
    estimated_financial_loss_prevented: float = 0.0
    quarkdown_report: str
