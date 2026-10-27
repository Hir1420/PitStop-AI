from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/api", tags=["System Health & Observability"])

@router.get("/health")
def health_check():
    """Basic service health endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "ai_engine": "Gemini Live API" if settings.GEMINI_API_KEY else "Deterministic Fallback & Rule-based NLP Engine",
        "simulation_mode": settings.SIMULATE_CALENDAR
    }

@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe checking database connectivity and core subsystems."""
    try:
        # Ping database
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ready" if db_status == "connected" else "not_ready",
        "database": db_status,
        "calendar_integration": "live" if settings.GOOGLE_CALENDAR_CLIENT_ID else "simulated",
        "weather_service": "open-meteo"
    }
