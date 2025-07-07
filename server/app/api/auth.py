import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError

from app.db.mongodb import db
from app.constants import COLLECTION_USERS, COLLECTION_CODES
from app.schema.auth import (
    RegisterRequest, RegisterResponse,
    VerifyRequest, VerifyResponse,
    LoginRequest, LoginResponse,
)
from app.core.config import settings
from app.utils.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper to hash passwords
def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)

@router.post(
        "/register",
        response_model=RegisterResponse,
        status_code=status.HTTP_201_CREATED,
)
async def register(
    req: RegisterRequest,
    background_tasks: BackgroundTasks
):
    """
    1) Ensure username/email not already taken.
    2) Create user with hashed password & email_verified=False.
    3) Generate a one‐time code & store with expiration.
    4) Send code via email in background.
    """
    uc = db[COLLECTION_USERS]

    # 1) uniqueness checks
    existing = await uc.find_one({"$or": [{"username": req.username}, {"email": req.email}]})
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # 2) insert user and generate verification code
    user = {
        "username": req.username,
        "password_hash": hash_password(req.password),
        "email": req.email,
        "email_verified": False,
        "created_at": datetime.utcnow(),
    }
    try:
        res = await uc.insert_one(user)
        user_id = res.inserted_id

        code = secrets.token_hex(3)  # 6 hex chars
        expires = datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
        await db[COLLECTION_CODES].insert_one({
            "user_id": user_id,
            "email": req.email,
            "code": code,
            "expires_at": expires,
            "created_at": datetime.utcnow(),
        })
    except DuplicateKeyError as e:
        raise HTTPException(status_code=400, detail="Username or email already exists") from e

    # 4) queue email send
    background_tasks.add_task(send_verification_email, req.email, code)

    return {"detail": "Verification code sent to your email"}

@router.post("/verify", response_model=VerifyResponse)
async def verify(req: VerifyRequest):
    """
    1) Look up code record by email.
    2) Reject if not found, wrong, or expired.
    3) Mark user.email_verified=True and delete code record.
    """
    coll = db[COLLECTION_CODES]
    record = await coll.find_one({"email": req.email, "code": req.code})

    if not record:
        raise HTTPException(status_code=400, detail="Invalid code")
    if record["expires_at"] < datetime.utcnow():
        # delete expired
        await coll.delete_one({"_id": record["_id"]})
        raise HTTPException(status_code=400, detail="Code has expired")

    # mark user
    await db[COLLECTION_USERS].update_one(
        {"_id": record["user_id"]},
        {"$set": {"email_verified": True}}
    )
    # remove used code
    await coll.delete_one({"_id": record["_id"]})

    return {"detail": "Email verified successfully"}

@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """
    1) Look up user by email.
    2) Reject if user not found or email not verified.
    3) Check password using bcrypt.
    4) Return success message (or token in future).
    """
    user = await db[COLLECTION_USERS].find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("email_verified", False):
        raise HTTPException(status_code=403, detail="Email not verified")

    print(f"hash password is: {user['password_hash']}")
    if not pwd_ctx.verify(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"detail": "Login successful"}
