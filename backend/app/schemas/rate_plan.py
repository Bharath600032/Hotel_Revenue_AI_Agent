"""
Pydantic v2 schemas for RatePlan master data.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RatePlanBase(BaseModel):
    rate_plan_code: str = Field(..., min_length=2, max_length=50)
    rate_plan_name: str = Field(..., min_length=2, max_length=100)
    meal_plan: str = Field(default="EP", max_length=50)  # EP, CP, MAP, AP
    cancellation_policy: str = Field(default="24_HOURS_FREE", max_length=255)
    refundable: bool = True
    multiplier: float = Field(default=1.0, gt=0.0)
    status: str = Field(default="ACTIVE", max_length=20)


class RatePlanCreate(RatePlanBase):
    pass


class RatePlanUpdate(BaseModel):
    rate_plan_name: Optional[str] = None
    meal_plan: Optional[str] = None
    cancellation_policy: Optional[str] = None
    refundable: Optional[bool] = None
    multiplier: Optional[float] = Field(default=None, gt=0.0)
    status: Optional[str] = None


class RatePlanResponse(RatePlanBase):
    model_config = ConfigDict(from_attributes=True)

    rate_plan_id: int
    hotel_id: int
