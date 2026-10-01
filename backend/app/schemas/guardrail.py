"""
Pydantic v2 schemas for Pricing Guardrails and Safety Validation.
"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class GuardrailValidationRequest(BaseModel):
    room_type_id: int
    stay_date: date
    proposed_rate: float = Field(..., gt=0.0)
    current_rate: float = Field(..., gt=0.0)


class GuardrailViolation(BaseModel):
    rule_name: str
    proposed_value: float
    limit_value: float
    message: str


class GuardrailValidationResponse(BaseModel):
    hotel_id: int
    room_type_id: int
    stay_date: date
    original_proposed_rate: float
    clamped_safe_rate: float
    was_clamped: bool
    requires_approval: bool
    violations: List[GuardrailViolation]
    status: str  # SAFE, CLAMPED, APPROVAL_REQUIRED, BLOCKED
