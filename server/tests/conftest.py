import json
import os
import sys
import pytest_asyncio
from bson import ObjectId
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from httpx._transports.asgi import ASGITransport
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from app.constants import COLLECTION_NAME

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "te_reo_maori_test_db")

@pytest_asyncio.fixture(scope="session")
async def db_client():
    """Create a MongoDB client for the test session."""
    client = AsyncIOMotorClient(MONGO_URI)
    yield client
    client.close()

@pytest_asyncio.fixture(scope="function")
async def clear_test_db(db_client):
    """Clear the test database before each test."""
    print(f"Clearing database: {DB_NAME}")
    await db_client.drop_database(DB_NAME)
    yield
    await db_client.drop_database(DB_NAME)

@pytest_asyncio.fixture(scope="session")
async def client():
    """Create an HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def seed_data(db_client):
    data_file = ROOT / "app" / "data" / "words.json"
    with open(data_file, encoding="utf-8") as f:
        words = json.load(f)

    docs = []
    for w in words:
        doc = {"_id": ObjectId(), **w}
        docs.append(doc)

    await db_client[DB_NAME][COLLECTION_NAME].insert_many(docs)
    return docs
