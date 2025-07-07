import pytest
from app.constants import COLLECTION_USERS, COLLECTION_CODES
from bson.objectid import ObjectId
from app.core.config import settings

@pytest.mark.asyncio
async def test_register_and_verify_flow(client, db_client, clear_test_db):
    # 1) register a new user
    payload = {
        "username": "alice",
        "email":    "alice@example.com",
        "password": "s3cret!"
    }
    r = await client.post("/auth/register", json=payload)
    assert r.status_code == 201
    assert r.json() == {"detail": "Verification code sent to your email"}

    # 2) check DB: one user, one code
    users = await db_client[settings.DB_NAME][COLLECTION_USERS].find().to_list(None)
    codes = await db_client[settings.DB_NAME][COLLECTION_CODES].find().to_list(None)
    assert len(users) == 1
    assert len(codes) == 1

    # 3) check our DummySMTP captured the email
    from tests.conftest import DummySMTP  # via the monkeypatched smtplib
    assert len(DummySMTP.sent) == 1
    email = DummySMTP.sent[0]
    assert email["to"] == "alice@example.com"
    assert "Your verification code is:" in email["body"]
    code = codes[0]["code"]

    # 4) now verify with correct code
    r2 = await client.post("/auth/verify", json={
        "email": "alice@example.com",
        "code":  code
    })
    assert r2.status_code == 200
    assert r2.json() == {"detail": "Email verified successfully"}

    # 5) user record should be marked verified
    user = await db_client[settings.DB_NAME][COLLECTION_USERS].find_one({"username": "alice"})
    assert user["email_verified"] is True

    # 6) code record should be deleted
    remaining = await db_client[settings.DB_NAME][COLLECTION_CODES].count_documents({})
    assert remaining == 0

@pytest.mark.asyncio
async def test_register_duplicate_username(client, db_client):
    # Pre-seed one user
    await db_client[settings.DB_NAME][COLLECTION_USERS].insert_one({
        "username": "bob",
        "password_hash": "x",
        "email": "bob@example.com",
        "email_verified": False,
        "created_at": None
    })

    r = await client.post("/auth/register", json={
        "username": "bob",
        "email":    "newbob@example.com",
        "password": "pw1234"
    })

    assert r.status_code == 400
    assert r.json()["detail"] == "Username or email already exists"
