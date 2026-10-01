"""
Pydantic v2 schemas for Pricing Engine recommendations.
"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PriceRecommendationRequest(BaseModel):
    room_type_id: int
    stay_date: date


class PriceRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: Optional[int] = None
    hotel_id: int
    room_type_id: int
    stay_date: date
    recommended_rate: float
    min_rate: float
    max_rate: float
    current_rate: float
    occupancy: float
    forecast_demand: float
    competitor_median: float
    demand_index: float
    price_reason: str
    confidence_score: float
    status: str
    requires_approval: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BatchRecommendationRequest(BaseModel):
    room_type_id: Optional[int] = None
    start_date: date
    days_count: int = Field(default=30, ge=1, le=365)


class BatchRecommendationResponse(BaseModel):
    hotel_id: int
    total_recommendations: int
    recommendations: List[PriceRecommendationResponse]
