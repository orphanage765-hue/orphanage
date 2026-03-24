from pydantic_settings import BaseSettings
from pathlib import Path

# Always find .env relative to this file's location, no matter where uvicorn is run from
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb+srv://anandhakrishnanr868_db_user:w7atCTWvuAmB4Par@agromarket.amjhuf7.mongodb.net/"
    DATABASE_NAME: str = "orphanage_db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Resend API (replaces SMTP)
    RESEND_API_KEY: str = ""
    MAIL_FROM: str = "onboarding@resend.dev"  # Change to your verified domain email later

    # Admin seed credentials
    ADMIN_EMAIL: str = "admin@orphanageapp.com"
    ADMIN_PASSWORD: str = "Admin@1234"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()
print(f"📧 Email configured: {'✅ Yes (Resend)' if settings.RESEND_API_KEY else '❌ No — set RESEND_API_KEY in .env'}")
