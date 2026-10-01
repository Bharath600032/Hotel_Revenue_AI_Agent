"""
Human Approval Workflow Service.
Handles manager rate approvals, overrides, rejections, and audit logging.
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.ai import PriceRecommendations
from app.models.audit import AuditLogs
from app.schemas.approval import ApprovalResponse
from app.core.exceptions import ResourceNotFoundError, DataValidationError


class ApprovalService:
    def get_pending_queue(self, db: Session, hotel_id: int) -> List[PriceRecommendations]:
        """Fetch all price recommendations requiring human approval."""
        return (
            db.query(PriceRecommendations)
            .filter(
                PriceRecommendations.hotel_id == hotel_id,
                PriceRecommendations.status == "PENDING",
            )
            .order_by(PriceRecommendations.stay_date)
            .all()
        )

    def approve_recommendation(
        self, db: Session, recommendation_id: int, user_id: int
    ) -> ApprovalResponse:
        """Approve recommended rate for production deployment."""
        rec = (
            db.query(PriceRecommendations)
            .filter(PriceRecommendations.recommendation_id == recommendation_id)
            .first()
        )
        if not rec:
            raise ResourceNotFoundError("PriceRecommendation", recommendation_id)

        now = datetime.now(timezone.utc)
        rec.status = "APPROVED"
        rec.approved_by = user_id
        rec.approved_at = now
        rec.requires_approval = False

        # Stage 4: Publish to RoomInventory
        inventory = (
            db.query(RoomInventory)
            .filter(
                RoomInventory.hotel_id == rec.hotel_id,
                RoomInventory.room_type_id == rec.room_type_id,
                RoomInventory.stay_date == rec.stay_date,
            )
            .first()
        )
        if inventory:
            inventory.current_rate = rec.recommended_rate

        rec.status = "PUBLISHED"

        audit = AuditLogs(
            user_id=user_id,
            action="APPROVE_AND_PUBLISH_PRICE",
            entity_type="PriceRecommendation",
            entity_id=str(recommendation_id),
            old_value={"status": "PENDING", "rate": rec.current_rate},
            new_value={"status": "PUBLISHED", "approved_by": user_id, "published_rate": rec.recommended_rate},
        )
        db.add(audit)
        db.commit()
        db.refresh(rec)

        return ApprovalResponse(
            recommendation_id=rec.recommendation_id,
            hotel_id=rec.hotel_id,
            room_type_id=rec.room_type_id,
            stay_date=str(rec.stay_date),
            current_rate=rec.current_rate,
            recommended_rate=rec.recommended_rate,
            final_rate=rec.recommended_rate,
            status="PUBLISHED",
            approved_by=user_id,
            approved_at=now,
            action_type="APPROVE_AND_PUBLISH",
            reason="Rate approved and published to inventory by Revenue Manager.",
        )

    def override_recommendation(
        self, db: Session, recommendation_id: int, user_id: int, override_rate: float, reason: str
    ) -> ApprovalResponse:
        """Apply manager custom rate override and publish to live inventory."""
        rec = (
            db.query(PriceRecommendations)
            .filter(PriceRecommendations.recommendation_id == recommendation_id)
            .first()
        )
        if not rec:
            raise ResourceNotFoundError("PriceRecommendation", recommendation_id)

        now = datetime.now(timezone.utc)
        old_rate = rec.recommended_rate
        rec.recommended_rate = override_rate
        rec.approved_by = user_id
        rec.approved_at = now
        rec.requires_approval = False
        rec.price_reason = f"MANAGEMENT OVERRIDE: {reason} (AI suggested ₹{old_rate:,.0f})"

        # Stage 4: Publish override to RoomInventory
        inventory = (
            db.query(RoomInventory)
            .filter(
                RoomInventory.hotel_id == rec.hotel_id,
                RoomInventory.room_type_id == rec.room_type_id,
                RoomInventory.stay_date == rec.stay_date,
            )
            .first()
        )
        if inventory:
            inventory.current_rate = override_rate

        rec.status = "PUBLISHED"

        audit = AuditLogs(
            user_id=user_id,
            action="OVERRIDE_AND_PUBLISH_PRICE",
            entity_type="PriceRecommendation",
            entity_id=str(recommendation_id),
            old_value={"recommended_rate": old_rate},
            new_value={"override_rate": override_rate, "reason": reason, "status": "PUBLISHED"},
        )
        db.add(audit)
        db.commit()
        db.refresh(rec)

        return ApprovalResponse(
            recommendation_id=rec.recommendation_id,
            hotel_id=rec.hotel_id,
            room_type_id=rec.room_type_id,
            stay_date=str(rec.stay_date),
            current_rate=rec.current_rate,
            recommended_rate=old_rate,
            final_rate=override_rate,
            status="PUBLISHED",
            approved_by=user_id,
            approved_at=now,
            action_type="OVERRIDE_AND_PUBLISH",
            reason=reason,
        )

    def reject_recommendation(
        self, db: Session, recommendation_id: int, user_id: int, reason: str
    ) -> ApprovalResponse:
        """Reject price recommendation."""
        rec = (
            db.query(PriceRecommendations)
            .filter(PriceRecommendations.recommendation_id == recommendation_id)
            .first()
        )
        if not rec:
            raise ResourceNotFoundError("PriceRecommendation", recommendation_id)

        now = datetime.now(timezone.utc)
        rec.status = "REJECTED"
        rec.approved_by = user_id
        rec.approved_at = now

        audit = AuditLogs(
            user_id=user_id,
            action="REJECT_PRICE_RECOMMENDATION",
            entity_type="PriceRecommendation",
            entity_id=str(recommendation_id),
            old_value={"status": rec.status},
            new_value={"status": "REJECTED", "reason": reason},
        )
        db.add(audit)
        db.commit()

        return ApprovalResponse(
            recommendation_id=rec.recommendation_id,
            hotel_id=rec.hotel_id,
            room_type_id=rec.room_type_id,
            stay_date=str(rec.stay_date),
            current_rate=rec.current_rate,
            recommended_rate=rec.recommended_rate,
            final_rate=rec.current_rate,
            status="REJECTED",
            approved_by=user_id,
            approved_at=now,
            action_type="REJECT",
            reason=reason,
        )

    def publish_recommendation(
        self, db: Session, recommendation_id: int, user_id: int
    ) -> ApprovalResponse:
        """Stage 4: Explicitly publish an approved rate to RoomInventory."""
        rec = (
            db.query(PriceRecommendations)
            .filter(PriceRecommendations.recommendation_id == recommendation_id)
            .first()
        )
        if not rec:
            raise ResourceNotFoundError("PriceRecommendation", recommendation_id)

        now = datetime.now(timezone.utc)
        inventory = (
            db.query(RoomInventory)
            .filter(
                RoomInventory.hotel_id == rec.hotel_id,
                RoomInventory.room_type_id == rec.room_type_id,
                RoomInventory.stay_date == rec.stay_date,
            )
            .first()
        )
        if inventory:
            inventory.current_rate = rec.recommended_rate

        rec.status = "PUBLISHED"
        rec.approved_at = now

        audit = AuditLogs(
            user_id=user_id,
            action="PUBLISH_PRICE_TO_INVENTORY",
            entity_type="PriceRecommendation",
            entity_id=str(recommendation_id),
            old_value={"current_rate": rec.current_rate},
            new_value={"published_rate": rec.recommended_rate, "status": "PUBLISHED"},
        )
        db.add(audit)
        db.commit()
        db.refresh(rec)

        return ApprovalResponse(
            recommendation_id=rec.recommendation_id,
            hotel_id=rec.hotel_id,
            room_type_id=rec.room_type_id,
            stay_date=str(rec.stay_date),
            current_rate=rec.current_rate,
            recommended_rate=rec.recommended_rate,
            final_rate=rec.recommended_rate,
            status="PUBLISHED",
            approved_by=user_id,
            approved_at=now,
            action_type="PUBLISH",
            reason="Rate published to live room inventory.",
        )


approval_service = ApprovalService()

