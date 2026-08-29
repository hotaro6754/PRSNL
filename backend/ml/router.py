import os
import time
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.contracts.observation import NetworkObservation
from backend.contracts.features import FeatureVector
from backend.contracts.prediction import MLPrediction
from backend.contracts.evidence import DetectionEvidence as EvidenceItem
from backend.ml.resolver import ModelResolver

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "window_duration", "packet_count", "byte_count", "src_packet_count",
    "dst_packet_count", "src_byte_count", "dst_byte_count", "packet_size_mean",
    "packet_size_std", "packet_size_min", "packet_size_max", "iat_mean",
    "iat_std", "iat_cv", "packet_rate", "byte_rate", "syn_ratio",
    "fin_ratio", "rst_ratio", "udp_ratio", "tcp_ratio", "icmp_ratio",
    "directionality", "fan_in", "fan_out", "dns_entropy", "tls_sni_entropy",
    "host_connections_5m", "host_unique_dests_5m", "host_unique_ports_5m",
    "host_dns_queries_5m", "host_tls_connections_5m", "host_bytes_out_5m",
    "host_bytes_in_5m"
]

def _fv_to_array(fv: FeatureVector) -> np.ndarray:
    row = []
    for col in FEATURE_COLUMNS:
        v = getattr(fv, col, None)
        row.append(float(v) if v is not None else 0.0)
    return np.array([row], dtype=np.float32)

class ModelRouter:
    """
    P3: Dynamic ML Router leveraging ModelResolver for hot swapping and canary routing.
    """
    def __init__(self, resolver: ModelResolver):
        self.resolver = resolver
        self.stage = "PRODUCTION"

    def evaluate(self, fv: FeatureVector, obs: NetworkObservation) -> Optional[MLPrediction]:
        X = _fv_to_array(fv)
        predictions: List[Dict[str, Any]] = []
        routing_key = obs.source_ip # Deterministic routing key

        # --- Supervised model ---
        xgb_model, xgb_meta, _ = self.resolver.get_routing("xgb_supervised", routing_key)
        if xgb_model is not None and xgb_meta is not None:
            try:
                t0 = time.perf_counter()
                proba = xgb_model.predict_proba(X)
                latency_ms = (time.perf_counter() - t0) * 1000
                attack_prob = float(proba[0][1]) if proba.shape[1] > 1 else float(proba[0][0])
                predictions.append({
                    "model": "xgb_supervised",
                    "model_id": xgb_meta.model_id,
                    "version": xgb_meta.model_version,
                    "stage": xgb_meta.stage.value,
                    "probability": attack_prob,
                    "latency_ms": latency_ms,
                })
            except Exception as e:
                logger.error(f"XGBoost inference failed for {xgb_meta.model_id} v{xgb_meta.model_version}: {e}")

        # --- Anomaly model ---
        iforest_model, iforest_meta, _ = self.resolver.get_routing("iforest_anomaly", routing_key)
        if iforest_model is not None and iforest_meta is not None:
            try:
                t0 = time.perf_counter()
                score = iforest_model.decision_function(X)
                latency_ms = (time.perf_counter() - t0) * 1000
                predictions.append({
                    "model": "iforest_anomaly",
                    "model_id": iforest_meta.model_id,
                    "version": iforest_meta.model_version,
                    "stage": iforest_meta.stage.value,
                    "score": float(score[0]),
                    "latency_ms": latency_ms,
                })
            except Exception as e:
                logger.error(f"IsolationForest inference failed for {iforest_meta.model_id} v{iforest_meta.model_version}: {e}")
                
        # --- Shadow Models (Executed but not returned for active detection) ---
        shadow_xgb, shadow_meta_xgb = self.resolver.get_shadow("xgb_supervised")
        if shadow_xgb:
             try:
                 t0_sh = time.perf_counter()
                 proba_sh = shadow_xgb.predict_proba(X)
                 latency_ms_sh = (time.perf_counter() - t0_sh) * 1000
                 attack_prob_sh = float(proba_sh[0][1]) if proba_sh.shape[1] > 1 else float(proba_sh[0][0])
                 predictions.append({
                     "model": "xgb_supervised_shadow",
                     "model_id": shadow_meta_xgb.model_id,
                     "version": shadow_meta_xgb.model_version,
                     "stage": shadow_meta_xgb.stage.value,
                     "probability": attack_prob_sh,
                     "latency_ms": latency_ms_sh,
                 })
             except Exception:
                 pass

        if not predictions:
            return None

        # Build output structure using active predictions
        return MLPrediction(
            timestamp=obs.timestamp,
            source_ip=obs.source_ip,
            destination_ip=obs.destination_ip,
            predictions=predictions,
            inference_latency_ms=0.0
        )

class EvidenceFusionEngine:
    """Remains functionally equivalent, uses the provided MLPrediction."""
    def fuse(self, det_alerts, ml_prediction: Optional[MLPrediction], root_obs: NetworkObservation):
        final_alerts = list(det_alerts)
        
        # Supervised Fusion
        xgb_pred = None
        if ml_prediction:
            xgb_pred = next((p for p in ml_prediction.predictions if p["model"] == "xgb_supervised"), None)
            
        if xgb_pred and xgb_pred["probability"] > 0.85:
            # We must use EvidenceItem
            ev = EvidenceItem(
                evidence_type="ML_SUPERVISED_ANOMALY",
                confidence=xgb_pred["probability"],
                description=f"High probability of malicious flow (XGB v{xgb_pred['version']})",
                model_version=xgb_pred["version"],
                raw_data=xgb_pred
            )
            from backend.contracts.alert import Alert, ThreatClass, Severity
            alert = Alert(
                source_ip=root_obs.source_ip,
                destination_ip=root_obs.destination_ip,
                destination_port=root_obs.destination_port,
                timestamp=root_obs.timestamp,
                threat_class=ThreatClass.ANOMALOUS_NETWORK_ACTIVITY,
                severity=Severity.HIGH,
                confidence=xgb_pred["probability"],
                evidence=[ev]
            )
            final_alerts.append(alert)
            
        return final_alerts
