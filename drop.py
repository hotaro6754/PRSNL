import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
async def drop():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await client.ndr_database.model_registry.drop()
asyncio.run(drop())
