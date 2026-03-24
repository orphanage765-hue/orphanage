from pydantic_settings import BaseSettings
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = ""
    DATABASE_NAME: str = "orphanage_db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Brevo (Sendinblue) Email API
    BREVO_API_KEY: str = ""
    MAIL_FROM: str = "orphanage765@gmail.com"

    # Admin seed credentials
    ADMIN_EMAIL: str = "admin@orphanageapp.com"
    ADMIN_PASSWORD: str = "Admin@1234"

    class Config:
        env_file = str(_ENV_FILE) if _ENV_FILE.exists() else None
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

_ok = bool(settings.BREVO_API_KEY)
print(f"📧 Brevo Email: {'✅ Configured' if _ok else '❌ Not configured — set BREVO_API_KEY in .env'}")
print(f"🗄️  MongoDB:    {settings.MONGODB_URL[:50]}...")
