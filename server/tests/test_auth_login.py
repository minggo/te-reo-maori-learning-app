import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.core.config import settings
from app.constants import COLLECTION_CODES, COLLECTION_USERS

@pytest.mark.asyncio
async def test_login_success(client, db_client, clear_test_db):
    # Step 1: Register a new user
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    res = await client.post("/auth/register", json=payload)
    assert res.status_code == 201

    # Step 2: Manually verify user in DB (simulate email verification)
    users = db_client[settings.DB_NAME][COLLECTION_USERS]
    user = await users.find_one({"username": "testuser"})
    assert user is not None
    await users.update_one({"_id": user["_id"]}, {"$set": {"email_verified": True}})

    # Step 3: Login with verified user
    login_payload = {
        "username": "testuser",
        "password": "securepassword123"
    }
    res = await client.post("/auth/login", json=login_payload)
    assert res.status_code == 200
    body = res.json()
    assert body["detail"] == "Login successful"
    assert body["user_id"] == str(user["_id"])


@pytest.mark.asyncio
async def test_login_fails_if_email_not_verified(client: AsyncClient, db_client, clear_test_db):
    # Register but don't verify
    payload = {
        "username": "unverified_user",
        "email": "unverified@example.com",
        "password": "password123"
    }
    res = await client.post("/auth/register", json=payload)
    assert res.status_code == 201

    # Attempt login
    login_payload = {
        "username": "unverified_user",
        "password": "password123"
    }
    res = await client.post("/auth/login", json=login_payload)
    assert res.status_code == 403
    assert res.json()["detail"] == "Email not verified"


@pytest.mark.asyncio
async def test_login_fails_with_wrong_password(client, db_client, clear_test_db):
    # Register and verify
    payload = {
        "username": "wrongpassuser",
        "email": "wrongpass@example.com",
        "password": "rightpass"
    }
    res = await client.post("/auth/register", json=payload)
    assert res.status_code == 201

    users = db_client[settings.DB_NAME][COLLECTION_USERS]
    user = await users.find_one({"username": "wrongpassuser"})
    await users.update_one({"_id": user["_id"]}, {"$set": {"email_verified": True}})

    # Try wrong password
    login_payload = {
        "username": "wrongpassuser",
        "password": "wrongpass"
    }
    res = await client.post("/auth/login", json=login_payload)
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid username or password"
