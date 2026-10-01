"""
Pydantic v2 schemas for Competitor Hotels, Competitor Rates, and Competitive Market Analysis.
"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CompetitorHotelBase(BaseModel):
    competitor_name: str = Field(..., min_length=2, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    star_rating: float = Field(default=4.0, ge=1.0, le=5.0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = Field(default="ACTIVE", max_length=20)


class CompetitorHotelCreate(CompetitorHotelBase):
    pass


class CompetitorHotelResponse(CompetitorHotelBase):
    model_config = ConfigDict(from_attributes=True)

    competitor_id: int
    hotel_id: int


class CompetitorRateBase(BaseModel):
    stay_date: date
    room_type: str = Field(default="Deluxe", max_length=100)
    rate: float = Field(..., gt=0.0)
    availability: bool = True
    meal_plan: str = Field(default="EP", max_length=50)
    cancellation_policy: str = Field(default="Standard", max_length=255)
    source: str = Field(default="OTA_FEED", max_length=50)


class CompetitorRateCreate(CompetitorRateBase):
    competitor_id: int


class CompetitorRateResponse(CompetitorRateBase):
    model_config = ConfigDict(from_attributes=True)

    competitor_rate_id: int
    competitor_id: int
    captured_at: datetime


class CompetitorOTARate(BaseModel):
    ota_name: str
    rate: float
    is_lowest: bool = False


class CompetitorRateInfo(BaseModel):
    competitor_id: int
    competitor_name: str
    rate: float
    lowest_ota_name: str = "Booking.com"
    ota_name: str = "Booking.com"
    source: str = "GOOGLE_LIVE"
    captured_at: Optional[str] = None
    ota_rates: List[CompetitorOTARate] = []



class CompetitorAnalysisResponse(BaseModel):
    hotel_id: int
    stay_date: date
    my_rate: float
    my_hotel_rate: float
    competitor_count: int
    competitor_rates: List[CompetitorRateInfo] = []
    competitor_median: float
    median_rate: float
    competitor_average: float
    competitor_min: float
    min_rate: float
    competitor_max: float
    max_rate: float
    price_gap_pct: float
    percentile_rank: float
    positioning: str = "Market Median Alignment"
    anomaly_detected: bool
    anomaly_reason: Optional[str] = None

