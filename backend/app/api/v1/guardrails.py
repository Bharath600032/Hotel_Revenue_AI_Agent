"""
Pricing Guardrails & Safety Controls REST API endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.guardrail import GuardrailValidationRequest, GuardrailValidationResponse
from app.services.pricing_guardrails import pricing_guardrails_engine
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}/guardrails", tags=["Pricing Guardrails"])


@router.post("/validate", response_model=GuardrailValidationResponse)
async def validate_guardrails(
    hotel_id: int,
    payload: GuardrailValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst"])),
):
    """Validate a proposed price recommendation against deterministic business safety guardrails."""
    verify_hotel_access(hotel_id, current_user)
    return pricing_guardrails_engine.validate_and_clamp_rate(
        db,
        hotel_id=hotel_id,
        room_type_id=payload.room_type_id,
        stay_date=payload.stay_date,
        proposed_rate=payload.proposed_rate,
        current_rate=payload.current_rate,
    )
