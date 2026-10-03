"""
Pydantic v2 schemas for Holidays, Events, and Calendar Demand Impact calculations.
"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class HolidayBase(BaseModel):
    country: str = Field(default="India", max_length=100)
    region: Optional[str] = Field(default=None, max_length=100)
    holiday_date: date
    holiday_name: str = Field(..., min_length=2, max_length=255)
    holiday_type: str = Field(default="NATIONAL", max_length=50)
    importance: int = Field(default=3, ge=1, le=5)


class HolidayCreate(HolidayBase):
    pass


class HolidayResponse(HolidayBase):
    model_config = ConfigDict(from_attributes=True)

    holiday_id: int


class EventBase(BaseModel):
    city: str = Field(..., min_length=2, max_length=100)
    event_name: str = Field(..., min_length=2, max_length=255)
    event_type: str = Field(default="CONFERENCE", max_length=50)
    start_date: date
    end_date: date
    expected_attendance: Optional[int] = Field(default=None, ge=0)
    venue: Optional[str] = Field(default=None, max_length=255)
    importance: int = Field(default=3, ge=1, le=5)
    source: str = Field(default="EVENT_FEED", max_length=50)


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    event_id: int


class CalendarImpactResponse(BaseModel):
    hotel_id: int
    stay_date: date
    active_holidays: List[HolidayResponse]
    active_events: List[EventResponse]
    holiday_demand_multiplier: float
    event_demand_multiplier: float
    weather_demand_multiplier: float = 1.0
    composite_demand_multiplier: float
    demand_classification: str  # NORMAL, MODERATE_UPLIFT, HIGH_DEMAND, EXTREME_DEMAND
    explanation: str
