"""
Pydantic v2 schemas for Revenue Calculation Engine outputs.
"""
from datetime import date
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RevenueSummary(BaseModel):
    hotel_id: int
    start_date: date
    end_date: date
    total_sellable_rooms: int
    total_occupied_rooms: int
    total_revenue: float
    occupancy_pct: float
    adr: float
    revpar: float
    trevpar: float
    cancellation_rate_pct: float
    average_lead_time_days: float


class PickupPace(BaseModel):
    hotel_id: int
    stay_date: date
    current_booked_rooms: int
    pickup_1d: int
    pickup_3d: int
    pickup_7d: int
    pickup_14d: int
    pickup_30d: int


class ChannelContribution(BaseModel):
    channel: str
    reservations_count: int
    total_revenue: float
    contribution_pct: float


class DayOfWeekPerformance(BaseModel):
    day_of_week: str  # Monday, Tuesday, ...
    day_index: int  # 0 to 6
    average_occupancy_pct: float
    average_adr: float
    average_revpar: float
    demand_factor: float
