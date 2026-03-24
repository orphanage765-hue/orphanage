from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

# Always find .env relative to this file's location
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb+srv://anandhakrishnanr868_db_user:w7atCTWvuAmB4Par@agromarket.amjhuf7.mongodb.net/"
    DATABASE_NAME: str = "orphanage_db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Brevo API (Replaces Resend/SMTP to bypass Render port blocking)
    BREVO_API_KEY: str = "" 
    
    # This MUST match your verified sender in Brevo (orphanage765@gmail.com)
    MAIL_FROM: str = "orphanage765@gmail.com"

    # Admin seed credentials
    ADMIN_EMAIL: str = "admin@orphanageapp.com"
    ADMIN_PASSWORD: str = "Admin@1234"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        # This allows the app to stay running even if variables are missing 
        # (useful for debugging during the demo)
        extra = "ignore" 

settings = Settings()

# Console log to verify status on Render startup
if settings.BREVO_API_KEY:
    print(f"📧 Email configured: ✅ Yes (Brevo API) - Sender: {settings.MAIL_FROM}")
else:
    print("📧 Email configured: ❌ No — Please set BREVO_API_KEY in Render Environment Variables")
