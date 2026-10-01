"""
Pricing Guardrails & Safety Controls Engine.
Enforces hard deterministic boundaries on all room pricing recommendations.
"""
from datetime import date, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.models.hotel import Hotel, RoomType
from app.models.rates import HistoricalRates
from app.schemas.guardrail import (
    GuardrailValidationRequest,
    GuardrailValidationResponse,
    GuardrailViolation,
)
from app.core.config import settings
from app.core.exceptions import ResourceNotFoundError


class PricingGuardrailsEngine:
    """Enforces non-bypassable business safety rules on proposed room rates."""

    def validate_and_clamp_rate(
        self,
        db: Session,
        hotel_id: int,
        room_type_id: int,
        stay_date: date,
        proposed_rate: float,
        current_rate: float,
    ) -> GuardrailValidationResponse:
        """
        Evaluate proposed rate against:
        1. Min Rate Floor
        2. Max Rate Ceiling
        3. Max Daily % Increase / Decrease Limit (e.g. max 20%)
        4. Human Approval Threshold (> 10% change)
        """
        room_type = db.query(RoomType).filter(RoomType.room_type_id == room_type_id).first()
        if not room_type:
            raise ResourceNotFoundError("RoomType", room_type_id)

        violations: List[GuardrailViolation] = []
        clamped_rate = proposed_rate
        was_clamped = False

        # Rule 1: Min Rate Floor
        min_floor = max(settings.DEFAULT_MIN_RATE_FLOOR, room_type.base_price * 0.70)
        if proposed_rate < min_floor:
            violations.append(
                GuardrailViolation(
                    rule_name="MIN_RATE_FLOOR",
                    proposed_value=proposed_rate,
                    limit_value=min_floor,
                    message=f"Proposed rate ₹{proposed_rate:,.0f} is below minimum rate floor ₹{min_floor:,.0f}.",
                )
            )
            clamped_rate = max(clamped_rate, min_floor)
            was_clamped = True

        # Rule 2: Max Rate Ceiling
        max_ceiling = min(settings.DEFAULT_MAX_RATE_CEILING, room_type.base_price * 2.50)
        if proposed_rate > max_ceiling:
            violations.append(
                GuardrailViolation(
                    rule_name="MAX_RATE_CEILING",
                    proposed_value=proposed_rate,
                    limit_value=max_ceiling,
                    message=f"Proposed rate ₹{proposed_rate:,.0f} exceeds maximum rate ceiling ₹{max_ceiling:,.0f}.",
                )
            )
            clamped_rate = min(clamped_rate, max_ceiling)
            was_clamped = True

        # Rule 3: Max Daily Change Limit (e.g., max 20% variation from current rate)
        max_increase = current_rate * (1.0 + settings.MAX_DAILY_PRICE_CHANGE_PCT)
        min_decrease = current_rate * (1.0 - settings.MAX_DAILY_PRICE_CHANGE_PCT)

        if clamped_rate > max_increase:
            violations.append(
                GuardrailViolation(
                    rule_name="MAX_DAILY_INCREASE_LIMIT",
                    proposed_value=clamped_rate,
                    limit_value=max_increase,
                    message=f"Rate increase exceeds maximum daily limit (+{settings.MAX_DAILY_PRICE_CHANGE_PCT * 100:.0f}%). Clamped from ₹{clamped_rate:,.0f} to ₹{max_increase:,.0f}.",
                )
            )
            clamped_rate = max_increase
            was_clamped = True
        elif clamped_rate < min_decrease:
            violations.append(
                GuardrailViolation(
                    rule_name="MAX_DAILY_DECREASE_LIMIT",
                    proposed_value=clamped_rate,
                    limit_value=min_decrease,
                    message=f"Rate decrease exceeds maximum daily limit (-{settings.MAX_DAILY_PRICE_CHANGE_PCT * 100:.0f}%). Clamped from ₹{clamped_rate:,.0f} to ₹{min_decrease:,.0f}.",
                )
            )
            clamped_rate = min_decrease
            was_clamped = True

        # Rule 4: Human Approval Threshold Check
        rate_diff_pct = abs(clamped_rate - current_rate) / current_rate
        requires_approval = rate_diff_pct >= settings.APPROVAL_THRESHOLD_PCT

        # Determine Final Status
        if was_clamped:
            status_str = "CLAMPED"
        elif requires_approval:
            status_str = "APPROVAL_REQUIRED"
        else:
            status_str = "SAFE"

        return GuardrailValidationResponse(
            hotel_id=hotel_id,
            room_type_id=room_type_id,
            stay_date=stay_date,
            original_proposed_rate=proposed_rate,
            clamped_safe_rate=round(clamped_rate, 0),
            was_clamped=was_clamped,
            requires_approval=requires_approval,
            violations=violations,
            status=status_str,
        )


pricing_guardrails_engine = PricingGuardrailsEngine()
