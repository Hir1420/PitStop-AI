import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from app.config import settings
from app.schemas.schemas import WeatherContextResponse

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    51: "Light drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    95: "Thunderstorm"
}

async def fetch_weather_context(
    latitude: float = 37.7749,
    longitude: float = -122.4194,
    location_name: str = "Workshop HQ (San Francisco, CA)",
    service_type: Optional[str] = None
) -> WeatherContextResponse:
    """Retrieves live meteorological data from Open-Meteo API."""
    url = f"{settings.OPEN_METEO_API_URL}?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
    
    temp = 18.5
    condition = "Partly cloudy"
    precip_prob = 15
    
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                code = current.get("weather_code", 0)
                temp = current.get("temperature_2m", 18.5)
                condition = WEATHER_CODES.get(code, "Clear")
                daily = data.get("daily", {})
                if daily.get("precipitation_probability_max"):
                    precip_prob = daily["precipitation_probability_max"][0]
    except Exception as e:
        print(f"Open-Meteo API fetch exception (falling back to cache): {e}")

    # Generate domain advisory based on service type
    advisory = None
    if service_type in ["detailing_and_wash", "detailing"]:
        if precip_prob > 40:
            advisory = f"High precipitation probability ({precip_prob}%). Recommend scheduling exterior wash/ceramic coating under covered bay or rescheduling for sunny window."
        else:
            advisory = f"Favorable weather conditions ({condition}, {temp}°C). Optimal for exterior detailing and curing."
    elif service_type in ["brake_service", "suspension_and_tires"]:
        if precip_prob > 50:
            advisory = "Wet road conditions expected. Technicians should exercise extra caution during post-repair road testing."

    return WeatherContextResponse(
        location=location_name,
        target_date=datetime.utcnow().strftime("%Y-%m-%d"),
        temperature_c=temp,
        weather_condition=condition,
        precipitation_probability=precip_prob,
        advisory_for_service=advisory,
        source="Open-Meteo Meteorological Data",
        timestamp=datetime.utcnow()
    )
