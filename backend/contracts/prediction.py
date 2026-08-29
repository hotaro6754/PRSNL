from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

class MLPrediction(BaseModel):
    """
    Schema boundary for ML integration, preserving model lineage and explainability.
    """
    model_id: str = Field(description="Unique identifier for the ML model")
    model_version: str = Field(description="Version of the model used for inference")
    feature_schema_version: str = Field(description="Version of the feature vector schema")
    training_dataset_version: Optional[str] = Field(None, description="Dataset version used for training")
    
    prediction: str = Field(description="Predicted class (e.g., 'PortScan', 'Benign')")
    raw_score: float = Field(description="Raw model output score (uncalibrated)")
    calibrated_probability: float = Field(description="Platt-scaled or isotonic calibrated probability")
    anomaly_score: Optional[float] = Field(None, description="Anomaly score from isolation forest/unsupervised models")
    
    inference_latency_ms: float = Field(description="Latency of the inference execution in milliseconds")
    inference_timestamp: float = Field(description="Timestamp when inference was performed")
    
    top_features: Dict[str, float] = Field(
        default_factory=dict, 
        description="Feature contributions (e.g., SHAP values) justifying the decision"
    )
