from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "te_reo_maori"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

print(f"🚨 Mongo client is using: {type(client)}")

