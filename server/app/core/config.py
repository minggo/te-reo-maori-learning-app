from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "te_reo_maori"

    # SMTP (for sending verification codes)
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str
    SMTP_SENDER: EmailStr

    # How long a code remains valid
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 10

settings = Settings()
