from pydantic import BaseModel, model_validator, Field
from typing import Any
from enum import Enum

class EvidenceClass(str, Enum):
    FACT = "FACT"
    OBSERVATION = "OBSERVATION"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"

class EvidenceQuality(BaseModel):
    reliability: float = 0.0
    freshness: float = 0.0
    directness: float = 0.0

class Provenance(BaseModel):
    source_event_id: str
    input_hash: str
    pipeline: str
    model_id: str
    model_version: str
    feature_schema_version: str

class CyberEvidence(BaseModel):
    """
    Evidence item with provenance for web analyzer.
    """
    url: str = ""
    evidence_type: str = ""
    evidence_class: EvidenceClass = EvidenceClass.OBSERVATION
    raw_input_hash: str = ""
    evidence_quality: EvidenceQuality = Field(default_factory=EvidenceQuality)
    details: dict = {}
    provenance: Provenance

    @model_validator(mode='after')
    def check_provenance(self):
        if not self.provenance:
            raise ValueError("Evidence missing provenance")
        return self

class DetectionEvidence(BaseModel):
    organization_id: str = "default_org"
    """
    Structured evidence produced by a detector.
    """
    feature: str
    value: Any
    contribution: float
    explanation: str = "Extracted passive feature"
    evidence_id: str = ""
    detector_id: str = ""
    detector_version: str = "1.0"
    category: str = "general"
    evidence_class: EvidenceClass = EvidenceClass.OBSERVATION
    raw_input_hash: str = ""
    evidence_quality: EvidenceQuality = Field(default_factory=EvidenceQuality)
    confidence: float = 0.0
    source: str = "unknown"
    provenance: str = "internal"
    crypto_provenance: Provenance = None
    observed_at: str = ""
