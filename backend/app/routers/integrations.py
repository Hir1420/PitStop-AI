from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.schemas import WeatherContextResponse
from app.services.weather_service import fetch_weather_context
from app.services.calendar_service import sync_appointment_to_calendar

router = APIRouter(prefix="/api/integrations", tags=["External Integrations"])

@router.get("/weather", response_model=WeatherContextResponse)
async def get_weather(
    latitude: float = 37.7749,
    longitude: float = -122.4194,
    location_name: str = "Workshop HQ (San Francisco, CA)",
    service_type: Optional[str] = None
):
    """Retrieves live meteorological conditions from Open-Meteo for weather-dependent workshop services."""
    return await fetch_weather_context(
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        service_type=service_type
    )

@router.post("/calendar/sync")
def trigger_calendar_sync(
    appointment_id: int,
    force_failure: bool = Query(False, description="Simulate remote integration failure to test resilience"),
    workshop_id: int = 1,
    db: Session = Depends(get_db)
):
    """Triggers calendar synchronization with failure simulation and retry recovery path."""
    try:
        result = sync_appointment_to_calendar(
            db=db,
            workshop_id=workshop_id,
            appointment_id=appointment_id,
            force_failure=force_failure
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
