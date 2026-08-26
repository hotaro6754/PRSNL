from pydantic import BaseModel
from typing import Any

class DetectionEvidence(BaseModel):
    """
    Structured evidence produced by a detector.
    """
    feature: str
    value: Any
    contribution: float
    explanation: str = "Extracted passive feature"
