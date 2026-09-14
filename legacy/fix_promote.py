import re

with open('backend/ml/registry.py', 'r') as f:
    content = f.read()

# Replace the entire promote_model block correctly
correct_block = '''
    async def promote_model(self, model_id: str, version: str, target_stage: ModelStage, actor: str, reason: str) -> bool:
        """
        Atomic state transition. If promoting to PRODUCTION, demotes the old PRODUCTION model.
        """
        model = await self.get_model(model_id, version)
        if not model:
            return False
            
        old_stage = model.stage
        
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                # If promoting to production, we must retire or shadow the current production model
                if target_stage == ModelStage.PRODUCTION:
                    current_prod = await self.collection.find_one({"model_type": model.model_type, "stage": ModelStage.PRODUCTION.value}, session=session)
                    if current_prod:
                        await self.collection.update_one(
                            {"_id": current_prod["_id"]},
                            {"\": {"stage": ModelStage.SHADOW.value, "retired_at": datetime.now(timezone.utc)}},
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
                    {"\": update_fields},
                    session=session
                )
                
                if res.modified_count == 1:
                    await self._audit(model_id, old_stage.value, version, "PROMOTE", actor, reason, "SUCCESS", target_stage.value)
                    return True
                return False
'''

# Use single quotes for the replacement string to avoid Powershell interpolation issues
correct_block = correct_block.replace('\', '')

# Extract from def promote_model to the end
idx = content.find('    async def promote_model')
if idx != -1:
    content = content[:idx] + correct_block.strip() + '\n'
    
with open('backend/ml/registry.py', 'w') as f:
    f.write(content)
