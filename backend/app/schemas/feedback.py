"""
Pydantic v2 schemas for Recommendation Feedback Loop & Model Analytics.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class FeedbackCreate(BaseModel):
    recommendation_id: int
    accepted: bool
    comments: Optional[str] = None
    actual_result: Optional[Dict[str, float]] = Field(
        default=None, description="Actual post-stay metrics: {actual_occupancy, actual_adr, actual_revenue}"
    )


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feedback_id: int
    recommendation_id: int
    user_id: int
    accepted: bool
    comments: Optional[str] = None
    actual_result: Optional[Dict[str, float]] = None
    created_at: datetime


class FeedbackAnalyticsResponse(BaseModel):
    hotel_id: int
    total_recommendations_count: int
    accepted_count: int
    rejected_count: int
    acceptance_rate_pct: float
    average_actual_occupancy_pct: float
    average_actual_adr: float
    comments_summary: List[str]
