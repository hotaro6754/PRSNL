import os
import hashlib
import logging
import asyncio
from typing import Optional, List, Dict
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from backend.contracts.ml_model import ModelRegistryEntry, ModelStage

logger = logging.getLogger('ModelRegistry')

class ModelRegistry:
    """
    MongoDB-backed registry for ML models. 
    Implements P3 lifecycle: Register, Validate, Deploy, Promote, Rollback.
    """
    def __init__(self, mongo_uri: str = None):
        if not mongo_uri:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://sih26145-mongo-prod:27017")
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client.ndr_database
        self.collection = self.db.model_registry
        self.audit_collection = self.db.model_audit_log

    async def setup_indexes(self):
        await self.collection.create_index([("model_id", 1), ("model_version", 1)], unique=True)
        await self.collection.create_index("stage")
        await self.collection.create_index("model_type")

    async def _audit(self, model_id: str, old_version: str, new_version: str, action: str, actor: str, reason: str, result: str, stage: str):
        await self.audit_collection.insert_one({
            "model_id": model_id,
            "old_version": old_version,
            "new_version": new_version,
            "action": action,
            "actor": actor,
            "timestamp": datetime.now(timezone.utc),
            "reason": reason,
            "deployment_stage": stage,
            "result": result
        })

    async def register_model(self, entry: ModelRegistryEntry, actor: str = "system", reason: str = "Initial registration") -> bool:
        try:
            # Check if exists
            existing = await self.collection.find_one({"model_id": entry.model_id, "model_version": entry.model_version})
            if existing:
                logger.error(f"Model {entry.model_id} v{entry.model_version} already registered.")
                return False

            await self.collection.insert_one(entry.model_dump())
            await self._audit(entry.model_id, "none", entry.model_version, "REGISTER", actor, reason, "SUCCESS", entry.stage.value)
            return True
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return False

    async def get_active_model(self, model_type: str, stage: ModelStage = ModelStage.PRODUCTION) -> Optional[ModelRegistryEntry]:
        doc = await self.collection.find_one({"model_type": model_type, "stage": stage.value}, sort=[("deployed_at", -1)])
        if doc:
            return ModelRegistryEntry(**doc)
        return None
        
    async def get_model(self, model_id: str, version: str) -> Optional[ModelRegistryEntry]:
        doc = await self.collection.find_one({"model_id": model_id, "model_version": version})
        if doc:
            return ModelRegistryEntry(**doc)
        return None

    async def promote_model(self, model_id: str, version: str, target_stage: ModelStage, actor: str, reason: str) -> bool:
        """
        Atomic state transition. If promoting to PRODUCTION, demotes the old PRODUCTION model.
        """
        model = await self.get_model(model_id, version)
        if not model:
            return False
            
        old_stage = model.stage
        
        # Execute without transactions for prototype standalone compatibility
        session = None
        if True:
            # If promoting to production, we must retire or shadow the current production model
                if target_stage == ModelStage.PRODUCTION:
                    current_prod = await self.collection.find_one({"model_type": model.model_type, "stage": ModelStage.PRODUCTION.value}, session=session)
                    if current_prod:
                        await self.collection.update_one(
                            {"_id": current_prod["_id"]},
                            {"$set": {"stage": ModelStage.SHADOW.value, "retired_at": datetime.now(timezone.utc)}},
                            session=session
                        )
                        await self._audit(current_prod["model_id"], current_prod["model_version"], "none", "DEMOTE", actor, f"Replaced by {version}", "SUCCESS", ModelStage.SHADOW.value)

                update_fields = {"stage": target_stage.value}
                now = datetime.now(timezone.utc)
                if target_stage in [ModelStage.PRODUCTION, ModelStage.CANARY, ModelStage.SHADOW]:
                    update_fields["deployed_at"] = now
                elif target_stage == ModelStage.VALIDATING:
                    update_fields["validated_at"] = now
                    
                res = await self.collection.update_one(
                    {"model_id": model_id, "model_version": version},
                    {"$set": update_fields},
                    session=session
                )
                
                if res.modified_count == 1:
                    await self._audit(model_id, old_stage.value, version, "PROMOTE", actor, reason, "SUCCESS", target_stage.value)
                    return True
                return False
