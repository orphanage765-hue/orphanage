from pydantic_settings import BaseSettings
from pathlib import Path

# Always find .env relative to this file's location, no matter where uvicorn is run from
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "orphanage_db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Gmail SMTP
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    # Admin seed credentials
    ADMIN_EMAIL: str = "admin@orphanageapp.com"
    ADMIN_PASSWORD: str = "Admin@1234"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()
print(f"📧 Email configured: {'✅ Yes' if settings.MAIL_FROM and '@' in settings.MAIL_FROM else '❌ No — check .env'}")
