import os
import hashlib
import joblib
import logging
import asyncio
from typing import Optional, Dict, Any, Tuple
import threading
from urllib.request import urlretrieve

from backend.contracts.ml_model import ModelRegistryEntry, ModelStage
from backend.ml.registry import ModelRegistry

logger = logging.getLogger('ModelResolver')

class ActiveModelCache:
    def __init__(self):
        self.production_model = None
        self.production_metadata: Optional[ModelRegistryEntry] = None
        
        self.canary_model = None
        self.canary_metadata: Optional[ModelRegistryEntry] = None
        
        self.shadow_model = None
        self.shadow_metadata: Optional[ModelRegistryEntry] = None
        
        self.lock = threading.RLock()

class ModelResolver:
    def __init__(self, registry: ModelRegistry, model_dir: str = "models"):
        self.registry = registry
        self.model_dir = model_dir
        self.caches: Dict[str, ActiveModelCache] = {
            "xgb_supervised": ActiveModelCache(),
            "iforest_anomaly": ActiveModelCache()
        }
        self.current_schema_version = "1.0"
        os.makedirs(self.model_dir, exist_ok=True)
        
    def _verify_sha256(self, filepath: str, expected_hash: str) -> bool:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() == expected_hash

    async def sync_models(self):
        """Polls the registry and hot-reloads models for PRODUCTION, CANARY, and SHADOW."""
        for m_type in self.caches.keys():
            try:
                prod = await self.registry.get_active_model(m_type, ModelStage.PRODUCTION)
                canary = await self.registry.get_active_model(m_type, ModelStage.CANARY)
                shadow = await self.registry.get_active_model(m_type, ModelStage.SHADOW)
                
                await self._sync_slot(m_type, prod, "production")
                await self._sync_slot(m_type, canary, "canary")
                await self._sync_slot(m_type, shadow, "shadow")
            except Exception as e:
                logger.error(f"Failed to sync model {m_type}: {e}", exc_info=True)

    async def _sync_slot(self, m_type: str, entry: Optional[ModelRegistryEntry], slot: str):
        cache = self.caches[m_type]
        
        with cache.lock:
            current_meta = getattr(cache, f"{slot}_metadata")
            
        if not entry:
            # If no model in this slot in DB, but we have one loaded, unload it
            if current_meta:
                with cache.lock:
                    setattr(cache, f"{slot}_model", None)
                    setattr(cache, f"{slot}_metadata", None)
                logger.info(f"Unloaded {slot} model for {m_type}")
            return
            
        if current_meta and current_meta.model_version == entry.model_version:
            # Check if canary rollout percentage changed!
            if slot == "canary" and current_meta.deployment_config.get("canary_percent") != entry.deployment_config.get("canary_percent"):
                with cache.lock:
                    setattr(cache, f"{slot}_metadata", entry)
                logger.info(f"Updated canary config for {m_type} v{entry.model_version}")
            return # Model code is up to date
            
        logger.info(f"New {slot} model detected for {m_type}: {entry.model_version}. Initiating hot load.")
        
        # 1. Schema compatibility check
        if entry.feature_schema_version != self.current_schema_version:
            logger.error(f"MODEL LOAD = FAIL. Incompatible schema {entry.feature_schema_version} != {self.current_schema_version}")
            return
            
        local_path = os.path.join(self.model_dir, f"{entry.model_id}_{entry.model_version}.pkl")
        if not os.path.exists(local_path):
            if entry.artifact_uri.startswith("http"):
                urlretrieve(entry.artifact_uri, local_path)
            elif entry.artifact_uri.startswith("file://"):
                import shutil
                shutil.copy2(entry.artifact_uri.replace("file://", ""), local_path)
            else:
                local_path = entry.artifact_uri
                
        if not os.path.exists(local_path):
             logger.error(f"MODEL LOAD = FAIL. Artifact not found at {local_path}")
             return

        if not self._verify_sha256(local_path, entry.artifact_sha256):
            logger.error(f"MODEL LOAD = FAIL. Checksum mismatch for {local_path}")
            return
            
        try:
            new_model = await asyncio.to_thread(joblib.load, local_path)
        except Exception as e:
            logger.error(f"MODEL LOAD = FAIL. Exception during load: {e}")
            return
            
        with cache.lock:
            setattr(cache, f"{slot}_model", new_model)
            setattr(cache, f"{slot}_metadata", entry)
            
        logger.info(f"Hot swap successful for {m_type} {slot} -> v{entry.model_version}")

    def get_routing(self, m_type: str, routing_key: str) -> Tuple[Optional[Any], Optional[ModelRegistryEntry], bool]:
        """
        Returns (model, metadata, is_shadow)
        If canary is active, routes deterministically based on hash of routing_key.
        """
        cache = self.caches.get(m_type)
        if not cache:
            return None, None, False
            
        with cache.lock:
            prod = (cache.production_model, cache.production_metadata)
            canary = (cache.canary_model, cache.canary_metadata)
            
            # Deterministic Canary Routing
            if canary[0] and canary[1]:
                pct = canary[1].deployment_config.get("canary_percent", 0)
                # hash modulo 100
                h = int(hashlib.md5(routing_key.encode()).hexdigest(), 16) % 100
                if h < pct:
                    return canary[0], canary[1], False
                    
            return prod[0], prod[1], False

    def get_shadow(self, m_type: str) -> Tuple[Optional[Any], Optional[ModelRegistryEntry]]:
        cache = self.caches.get(m_type)
        if not cache:
            return None, None
        with cache.lock:
            return cache.shadow_model, cache.shadow_metadata
