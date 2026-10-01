"""
Pydantic v2 schemas for Hotel master data.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class HotelBase(BaseModel):
    hotel_code: str = Field(..., min_length=2, max_length=50)
    hotel_name: str = Field(..., min_length=2, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    country: str = Field(default="India", max_length=100)
    timezone: str = Field(default="Asia/Kolkata", max_length=50)
    currency: str = Field(default="INR", max_length=10)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_rooms: int = Field(default=100, ge=1)
    star_rating: Optional[float] = Field(default=4.0, ge=1.0, le=5.0)
    min_price_floor: Optional[float] = Field(default=3000.0, ge=0.0)
    max_price_ceiling: Optional[float] = Field(default=30000.0, ge=0.0)
    status: str = Field(default="ACTIVE", max_length=20)


class HotelCreate(HotelBase):
    pass


class HotelUpdate(BaseModel):
    hotel_code: Optional[str] = None
    hotel_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_rooms: Optional[int] = Field(default=None, ge=1)
    star_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    min_price_floor: Optional[float] = Field(default=None, ge=0.0)
    max_price_ceiling: Optional[float] = Field(default=None, ge=0.0)
    max_daily_price_change_pct: Optional[float] = Field(default=None, ge=0.0)
    status: Optional[str] = None


class HotelResponse(HotelBase):
    model_config = ConfigDict(from_attributes=True)

    hotel_id: int
