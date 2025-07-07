import pytest
from app.constants import COLLECTION_USERS, COLLECTION_CODES
from app.core.config import settings
from pymongo.errors import DuplicateKeyError

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

@pytest.mark.asyncio
async def test_register_with_duplicate_email(client, db_client, clear_test_db):
    # Step 1: Register a new user (initial registration)
    payload = {
        "username": "testuser1",
        "email": "test@example.com",
        "password": "securepassword123"
    }

    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201  # First registration should succeed

    # Step 2: Attempt to register again with the same email (different username)
    duplicate_payload = {
        "username": "testuser2",              # New username
        "email": "test@example.com",          # Same email as before
        "password": "anotherpassword456"
    }

    response = await client.post("/auth/register", json=duplicate_payload)

    # Step 3: Expect a 400 error due to duplicate email
    assert response.status_code == 400
    assert response.json()["detail"] == "Username or email already exists"

    # Step 4: Ensure only one user with the email exists in the database
    users = await db_client[settings.DB_NAME]["users"].find({"email": "test@example.com"}).to_list(length=10)
    assert len(users) == 1  # No additional user should be created

    # Step 5: Ensure only one verification code was created
    codes = await db_client[settings.DB_NAME][COLLECTION_CODES].find({"email": "test@example.com"}).to_list(length=10)
    assert len(codes) == 1  # No duplicate verification code should be inserted

