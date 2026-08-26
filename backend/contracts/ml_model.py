from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class ModelStage(str, Enum):
    TRAINING = "TRAINING"
    VALIDATING = "VALIDATING"
    SHADOW = "SHADOW"
    CANARY = "CANARY"
    PRODUCTION = "PRODUCTION"
    RETIRED = "RETIRED"
    FAILED = "FAILED"

class ModelRegistryEntry(BaseModel):
    model_id: str
    model_version: str
    model_type: str = Field(..., description="e.g. xgb_supervised, iforest_anomaly")
    stage: ModelStage
    
    feature_schema_version: str
    extractor_version: str
    dataset_version: Optional[str] = None
    training_run_id: Optional[str] = None
    calibration_version: Optional[str] = None
    
    artifact_uri: str
    artifact_sha256: str
    
    created_at: datetime
    validated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    retired_at: Optional[datetime] = None
    
    metrics: Dict[str, Any] = Field(default_factory=dict)
    owner: str = "system"
    deployment_config: Dict[str, Any] = Field(default_factory=dict)
