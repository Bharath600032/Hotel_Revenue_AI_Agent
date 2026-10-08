"""
Pydantic v2 schemas for Length of Stay (LOS) Rules & Group Displacement Analysis.
"""
from typing import Optional, List, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator


class GroupDisplacementRequest(BaseModel):
    hotel_id: Optional[int] = Field(None, description="Hotel ID")
    group_name: Optional[str] = Field("Corporate Group Lead", description="Name of corporate or group entity")
    room_type_id: Optional[int] = Field(None, description="Target Room Type ID")
    rooms_requested: int = Field(..., ge=1, le=500, description="Number of rooms requested per night")
    
    # Accept checkin_date OR start_date
    checkin_date: Optional[str] = Field(None, description="Check-in date YYYY-MM-DD")
    start_date: Optional[str] = Field(None, description="Start date YYYY-MM-DD")
    
    # Accept checkout_date OR end_date
    checkout_date: Optional[str] = Field(None, description="Check-out date YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="End date YYYY-MM-DD")
    
    offered_rate: float = Field(..., gt=0.0, description="Offered room rate per room night (₹)")
    f_and_b_revenue: Optional[float] = Field(0.0, ge=0.0, description="Estimated F&B revenue spend (₹)")
    meeting_room_rental: Optional[float] = Field(0.0, ge=0.0, description="Meeting room rental spend (₹)")
    other_ancillary_revenue: Optional[float] = Field(0.0, ge=0.0, description="Other ancillary spend (₹)")

    @model_validator(mode="before")
    @classmethod
    def normalize_dates(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("checkin_date") and data.get("start_date"):
                data["checkin_date"] = data["start_date"]
            if not data.get("checkout_date") and data.get("end_date"):
                data["checkout_date"] = data["end_date"]
        return data


class DailyDisplacementBreakdown(BaseModel):
    stay_date: str
    transient_rate: float
    transient_demand_pct: float
    available_capacity: int
    group_rooms: int
    displaced_transient_rooms: int
    transient_revenue_lost: float


class GroupDisplacementResponse(BaseModel):
    hotel_id: int
    room_type_id: Optional[int] = None
    group_name: str
    rooms_requested: int
    checkin_date: str
    checkout_date: str
    start_date: str
    end_date: str
    nights: int
    total_nights: int
    total_room_nights: int
    total_room_nights_requested: int
    offered_rate: float
    offered_group_rate: float
    proposed_group_revenue: float
    gross_group_room_revenue: float
    ancillary_revenue: float
    total_gross_group_revenue: float
    transient_revenue_displaced: float
    total_transient_revenue_displaced: float
    net_displacement_impact: float
    net_revenue_impact: float
    breakeven_group_rate: float
    counter_offer_rate: float
    recommended_counter_offer_rate: float
    decision: str  # ACCEPT, REJECT, COUNTER_OFFER
    recommendation: str  # ACCEPT, REJECT, COUNTER_OFFER
    rationale: str
    decision_rationale: str
    daily_breakdown: List[DailyDisplacementBreakdown] = []
    displacement_id: Optional[int] = None
    created_at: Optional[datetime] = None


class LOSRuleBase(BaseModel):
    stay_date: str
    min_length_of_stay: int = Field(default=1, ge=1, le=30)
    max_length_of_stay: Optional[int] = Field(default=None, ge=1, le=30)
    closed_to_arrival: bool = False
    closed_to_departure: bool = False
    reason: Optional[str] = None


class LOSRuleUpdate(BaseModel):
    min_length_of_stay: Optional[int] = Field(default=None, ge=1, le=30)
    max_length_of_stay: Optional[int] = Field(default=None, ge=1, le=30)
    closed_to_arrival: Optional[bool] = None
    closed_to_departure: Optional[bool] = None
    reason: Optional[str] = None


class LOSRuleResponse(LOSRuleBase):
    model_config = ConfigDict(from_attributes=True)

    rule_id: int = 0
    los_rule_id: Optional[int] = 0
    hotel_id: int
    room_type_id: Optional[int] = None
    is_system_recommended: bool = False
    ai_confidence: Optional[float] = 0.95
    recommendation_reason: Optional[str] = None
