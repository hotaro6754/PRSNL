from abc import ABC, abstractmethod
from typing import List, Optional
from backend.contracts.alert import Alert
from backend.contracts.evidence import DetectionEvidence
from backend.contracts.observation import NetworkObservation

class BaseDetector(ABC):
    """
    BaseDetector enforces strict passive tumbling-window constraints.
    It relies on the WindowManager to aggregate flows, and processes them as a batch.
    """

    def __init__(self, window_size_ms: int, detector_id: str):
        self.window_size_ms = window_size_ms
        self.detector_id = detector_id

    @abstractmethod
    def evaluate_window(self, flows: List[NetworkObservation], window_start_ms: int) -> List[Alert]:
        """
        Evaluates a complete batch of flows for a tumbling window.
        """
        pass

    def calculate_observability(self, flow: Optional[NetworkObservation]) -> float:
        if not flow:
            return 0.5
            
        fwd_bytes = flow.src2dst_bytes or 0
        bwd_bytes = flow.dst2src_bytes or 0
        
        if fwd_bytes == 0 and bwd_bytes == 0:
            return 0.0
        
        if fwd_bytes == 0 or bwd_bytes == 0:
            return 0.5
            
        return 1.0
