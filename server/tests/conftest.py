import pytest
import pytest_asyncio
from bson import ObjectId
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from httpx._transports.asgi import ASGITransport
from app.data.loader import load_words_from_file

from app.main import app
from app.constants import COLLECTION_NAME
from app.core.config import settings
from app.utils.email import smtplib as email_smtplib
from tests.dummy_smtp import DummySMTP

@pytest.fixture(autouse=True)
def stub_hash(monkeypatch):
    # return unhashed password so you don't need bcrypt in tests
    monkeypatch.setattr("app.api.auth.hash_password", lambda pw: pw)
    monkeypatch.setattr("app.api.auth.pwd_ctx.verify", lambda raw, hashed: hashed == raw)

@pytest.fixture(autouse=True)
def reset_and_patch_smtp(monkeypatch):
    # clear any old messages
    DummySMTP.sent.clear()
    # patch the app’s SMTP
    monkeypatch.setattr(email_smtplib, "SMTP", DummySMTP)
    yield

@pytest_asyncio.fixture(scope="session")
async def db_client():
    """Create a MongoDB client for the test session."""
    client = AsyncIOMotorClient(settings.MONGO_URI)
    yield client
    client.close()

@pytest_asyncio.fixture(scope="function")
async def clear_test_db(db_client):
    """Clear the test database before each test."""
    print(f"Clearing database: {settings.DB_NAME}")
    await db_client.drop_database(settings.DB_NAME)
    yield
    await db_client.drop_database(settings.DB_NAME)

@pytest_asyncio.fixture(scope="session")
async def client():
    """Create an HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def seed_data(db_client):
    words = load_words_from_file()

    docs = []
    for w in words:
        doc = {"_id": ObjectId(), **w}
        docs.append(doc)

    await db_client[settings.DB_NAME][COLLECTION_NAME].insert_many(docs)
    return docs
