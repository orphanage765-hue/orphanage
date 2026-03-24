from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

# Find .env relative to this file
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb+srv://anandhakrishnanr868_db_user:w7atCTWvuAmB4Par@agromarket.amjhuf7.mongodb.net/"
    DATABASE_NAME: str = "orphanage_db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Brevo API Configuration
    # If Render Env Var fails, you can paste your key inside the quotes below as a last resort
    BREVO_API_KEY: str = "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" 
    
    # Must match your verified Brevo sender: orphanage765@gmail.com
    MAIL_FROM: str = "orphanage765@gmail.com"

    # Admin seed credentials
    ADMIN_EMAIL: str = "admin@orphanageapp.com"
    ADMIN_PASSWORD: str = "Admin@1234"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore" 

settings = Settings()

# CRITICAL FOR DEMO: Check logs to see if the key is actually loaded
if settings.BREVO_API_KEY:
    # Prints only the first 4 characters for security, helps confirm it's not empty
    print(f"📧 Email System: Initialized with Key starting with '{settings.BREVO_API_KEY[:4]}...'")
else:
    print("📧 Email System: ❌ ERROR - BREVO_API_KEY is missing!")
