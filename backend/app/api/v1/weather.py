"""
Weather Intelligence REST API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.weather import WeatherForecastResponse
from app.weather.engine import weather_engine
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}/weather", tags=["Weather Intelligence"])


@router.get("", response_model=WeatherForecastResponse)
async def get_weather_forecast(
    hotel_id: int,
    days: int = Query(14, ge=1, le=14, description="Forecast horizon days (7 or 14 days)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """
    Fetch 7-day or 14-day weather forecast and daily demand multipliers for hotel property.
    Integrates with Open-Meteo Free Weather API with automatic city geocoding & seasonal fallback.
    """
    verify_hotel_access(hotel_id, current_user, db)
    return weather_engine.get_weather_forecast_for_hotel(db, hotel_id=hotel_id, horizon_days=days)
