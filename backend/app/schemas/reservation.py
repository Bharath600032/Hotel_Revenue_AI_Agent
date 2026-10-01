"""
Pydantic v2 schemas for Reservation entities.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ReservationBase(BaseModel):
    reservation_code: str = Field(..., min_length=2, max_length=50)
    booking_date: date
    checkin_date: date
    checkout_date: date
    rooms_booked: int = Field(default=1, ge=1)
    adults: int = Field(default=2, ge=1)
    children: int = Field(default=0, ge=0)
    booking_channel: str = Field(default="Direct", max_length=50)
    reservation_status: str = Field(default="CONFIRMED", max_length=30)  # CONFIRMED, CANCELLED, NO_SHOW, CHECKED_OUT
    room_rate: float = Field(..., gt=0.0)
    total_amount: float = Field(..., gt=0.0)


class ReservationCreate(ReservationBase):
    room_type_id: int
    rate_plan_id: int


class ReservationUpdate(BaseModel):
    reservation_status: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    room_rate: Optional[float] = Field(default=None, gt=0.0)
    total_amount: Optional[float] = Field(default=None, gt=0.0)


class ReservationResponse(ReservationBase):
    model_config = ConfigDict(from_attributes=True)

    reservation_id: int
    hotel_id: int
    room_type_id: int
    rate_plan_id: int
    cancelled_at: Optional[datetime] = None
