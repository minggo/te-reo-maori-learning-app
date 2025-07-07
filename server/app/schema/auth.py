from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr

class VerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)

class RegisterResponse(BaseModel):
    detail: str

class VerifyResponse(BaseModel):
    detail: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    detail: str