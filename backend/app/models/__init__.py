"""
Central export for all SQLAlchemy ORM models.
Provides both plural and singular aliases for model references.
"""
from app.db.base import Base
from app.models.user import User
from app.models.hotel import Hotel, RoomType, RatePlan
from app.models.inventory import RoomInventory, Reservation, DailyBookingSnapshot
from app.models.rates import HistoricalRates, CompetitorHotels, CompetitorRates
from app.models.events import Holidays, Events, Weather
from app.models.ai import (
    Forecasts,
    PriceRecommendations,
    AgentRuns,
    AgentToolCalls,
    ModelRegistry,
    Feedback,
)
from app.models.audit import AuditLogs

# Singular aliases for clean domain model imports
HistoricalRate = HistoricalRates
CompetitorHotel = CompetitorHotels
CompetitorRate = CompetitorRates
Holiday = Holidays
Event = Events
WeatherForecast = Weather
Forecast = Forecasts
PriceRecommendation = PriceRecommendations
AuditLog = AuditLogs

__all__ = [
    "Base",
    "User",
    "Hotel",
    "RoomType",
    "RatePlan",
    "RoomInventory",
    "Reservation",
    "DailyBookingSnapshot",
    "HistoricalRates",
    "HistoricalRate",
    "CompetitorHotels",
    "CompetitorHotel",
    "CompetitorRates",
    "CompetitorRate",
    "Holidays",
    "Holiday",
    "Events",
    "Event",
    "Weather",
    "WeatherForecast",
    "Forecasts",
    "Forecast",
    "PriceRecommendations",
    "PriceRecommendation",
    "AgentRuns",
    "AgentToolCalls",
    "ModelRegistry",
    "Feedback",
    "AuditLogs",
    "AuditLog",
]
