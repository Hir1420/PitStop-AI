import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "PitStop AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    SECRET_KEY: str = "pitstop-ai-dev-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "sqlite:///./pitstop.db"
    
    # AI (Gemini)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # External APIs
    OPEN_METEO_API_URL: str = "https://api.open-meteo.com/v1/forecast"
    GOOGLE_CALENDAR_CLIENT_ID: Optional[str] = None
    GOOGLE_CALENDAR_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CALENDAR_REDIRECT_URI: str = "http://localhost:8000/api/integrations/calendar/callback"
    SIMULATE_CALENDAR: bool = True
    
    # Real Email Delivery (Resend API & SMTP)
    RESEND_API_KEY: Optional[str] = None
    RESEND_FROM: str = "PitStop AI <onboarding@resend.dev>"
    
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "PitStop AI Workshop"
    
    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }

settings = Settings()
