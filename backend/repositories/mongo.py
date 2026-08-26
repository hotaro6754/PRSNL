"""
Real MongoDB repository using motor (async) for production and
pymongo (sync) for scripts/tests.

Falls back to a durable file buffer if MongoDB is unreachable,
so the detection plane never stops because Mongo is down, 
but without silently dropping persistence.
"""
import os
import json
import time
import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

import motor.motor_asyncio
import aiofiles

from backend.config import ENVIRONMENT, AppEnv, BUFFER_DIR

logger = logging.getLogger(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.environ.get("MONGO_DB", "sih26145")

class MongoRepository:
    def __init__(self, uri=MONGO_URI, db_name=MONGO_DB):
        self.uri = uri
        self.db_name = db_name
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.uri, serverSelectionTimeoutMS=3000)
        self.db = self.client[self.db_name]
        
        self.alerts = self.db["alerts"]
        self.cases = self.db["cases"]
        self.ml_predictions = self.db["ml_predictions"]
        self.mcp_executions = self.db["mcp_executions"]
        self.audit_events = self.db["audit_events"]
        self.model_registry = self.db["model_registry"]
        
        self.fallback_buffer_file = os.path.join(BUFFER_DIR, "mongo_fallback.jsonl")
        
        # Test connection in background
        self._connected = False
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._ping())
        except RuntimeError:
            pass

    async def _ping(self):
        try:
            await self.client.admin.command('ping')
            self._connected = True
            logger.info(f"MongoDB connected: {self.uri} / {self.db_name}")
        except Exception as e:
            self._connected = False
            if ENVIRONMENT == AppEnv.PRODUCTION:
                logger.error(f"MongoDB unavailable in PRODUCTION: {e} - relying on durable buffer")
            else:
                logger.warning(f"MongoDB connection failed in {ENVIRONMENT.value}: {e} - using durable buffer")

    async def _write_buffer(self, collection: str, data: dict):
        """Durable append-only buffer for persistence when Mongo is down"""
        record = {
            "timestamp": time.time(),
            "collection": collection,
            "data": data
        }
        try:
            async with aiofiles.open(self.fallback_buffer_file, mode='a') as f:
                await f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"CRITICAL: Failed to write to durable buffer: {e}")

    # ── Alerts ─────────────────────────────────────────────────────────
    async def save_alert(self, alert_dict: Dict[str, Any]) -> None:
        try:
            await self.alerts.insert_one(alert_dict)
        except Exception as e:
            logger.error(f"Mongo save_alert failed: {e} - queuing to durable buffer")
            await self._write_buffer("alerts", alert_dict)

    # ── Cases ──────────────────────────────────────────────────────────
    async def upsert_case(self, case_dict: Dict[str, Any]) -> None:
        try:
            await self.cases.replace_one(
                {"case_id": case_dict.get("case_id")}, 
                case_dict, 
                upsert=True
            )
        except Exception as e:
            logger.error(f"Mongo upsert_case failed: {e} - queuing to durable buffer")
            await self._write_buffer("cases", case_dict)

    async def get_active_cases(self) -> List[Dict]:
        try:
            cursor = self.cases.find({"status": "OPEN"})
            return await cursor.to_list(length=500)
        except Exception as e:
            logger.error(f"Mongo get_active_cases failed: {e}")
            # In production, if Mongo is down, we can't reliably get state. Return empty.
            return []

    # ── ML Predictions ─────────────────────────────────────────────────
    async def save_prediction(self, pred_dict: Dict[str, Any]) -> None:
        try:
            await self.ml_predictions.insert_one(pred_dict)
        except Exception as e:
            logger.error(f"Mongo save_prediction failed: {e} - queuing to durable buffer")
            await self._write_buffer("ml_predictions", pred_dict)

    # ── Audit Events ───────────────────────────────────────────────────
    async def log_audit(self, event: Dict[str, Any]) -> None:
        event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        try:
            await self.audit_events.insert_one(event)
        except Exception as e:
            logger.error(f"Mongo audit log failed: {e} - queuing to durable buffer")
            await self._write_buffer("audit_events", event)

    # ── Model Registry ─────────────────────────────────────────────────
    async def save_model_metadata(self, meta: Dict[str, Any]) -> None:
        model_id = meta.get("model_id", "")
        version = meta.get("version", "")
        try:
            await self.model_registry.replace_one(
                {"model_id": model_id, "version": version},
                meta,
                upsert=True,
            )
        except Exception as e:
            logger.error(f"Mongo save_model_metadata failed: {e}")

    # ── MCP Tool Executions ────────────────────────────────────────────
    async def save_mcp_execution(self, execution: Dict[str, Any]) -> None:
        try:
            await self.mcp_executions.insert_one(execution)
        except Exception as e:
            logger.error(f"Mongo save_mcp_execution failed: {e} - queuing to durable buffer")
            await self._write_buffer("mcp_executions", execution)

    # ── Health ─────────────────────────────────────────────────────────
    async def health(self) -> Dict[str, Any]:
        try:
            await self.client.admin.command("ping")
            return {"status": "connected", "uri": self.uri, "db": self.db_name}
        except Exception as e:
            buffer_size = 0
            if os.path.exists(self.fallback_buffer_file):
                buffer_size = os.path.getsize(self.fallback_buffer_file)
            return {"status": "degraded_or_failed", "error": str(e), "buffer_size_bytes": buffer_size}
