from motor.motor_asyncio import AsyncIOMotorClient
import os
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
