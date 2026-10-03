"""
Pydantic v2 schemas for Weather Forecasts and Weather Demand Multipliers.
"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class DailyWeatherForecast(BaseModel):
    stay_date: date
    city: str
    condition: str
    weather_code: int
    temp_max_c: float
    temp_min_c: float
    precipitation_mm: float
    weather_multiplier: float
    weather_impact: str  # POSITIVE_DEMAND, NEUTRAL, DEPRESSED_DEMAND
    explanation: str


class WeatherForecastResponse(BaseModel):
    hotel_id: int
    hotel_name: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    forecast_horizon_days: int
    daily_forecasts: List[DailyWeatherForecast]
    average_weather_multiplier: float
    provider: str = "Open-Meteo Free Weather API"
