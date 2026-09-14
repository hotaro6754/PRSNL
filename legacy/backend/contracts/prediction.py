from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

class MLPrediction(BaseModel):
    """
    Schema boundary for ML integration, preserving model lineage and explainability.
    """
    timestamp: float
    source_ip: str
    destination_ip: str
    predictions: list
    inference_latency_ms: float
