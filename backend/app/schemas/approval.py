"""
Pydantic v2 schemas for Human Approval Workflow management.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class OverrideRequest(BaseModel):
    override_rate: float = Field(..., gt=0.0, description="Manager custom rate override")
    reason: str = Field(..., min_length=2, description="Reason for manager rate override")


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=2, description="Reason for rejecting recommendation")


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: int
    hotel_id: int
    room_type_id: int
    stay_date: str
    current_rate: float
    recommended_rate: float
    final_rate: float
    status: str  # APPROVED, REJECTED, OVERRIDDEN
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    action_type: str
    reason: Optional[str] = None
