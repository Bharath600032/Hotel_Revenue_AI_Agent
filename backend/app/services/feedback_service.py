"""
Feedback Loop & Model Analytics Service.
Collects manager feedback, logs post-stay actual outcomes, and computes acceptance metrics.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.ai import Feedback, PriceRecommendations
from app.models.audit import AuditLogs
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackAnalyticsResponse
from app.core.exceptions import ResourceNotFoundError


class FeedbackService:
    def submit_feedback(
        self, db: Session, hotel_id: int, user_id: int, fb_in: FeedbackCreate
    ) -> FeedbackResponse:
        rec = (
            db.query(PriceRecommendations)
            .filter(PriceRecommendations.recommendation_id == fb_in.recommendation_id)
            .first()
        )
        if not rec:
            raise ResourceNotFoundError("PriceRecommendation", fb_in.recommendation_id)

        fb = Feedback(
            recommendation_id=fb_in.recommendation_id,
            user_id=user_id,
            accepted=fb_in.accepted,
            comments=fb_in.comments,
            actual_result=fb_in.actual_result,
        )
        db.add(fb)

        # Update recommendation status
        rec.status = "APPROVED" if fb_in.accepted else "REJECTED"

        audit = AuditLogs(
            user_id=user_id,
            action="SUBMIT_RECOMMENDATION_FEEDBACK",
            entity_type="Feedback",
            entity_id=str(fb_in.recommendation_id),
            new_value={"accepted": fb_in.accepted, "comments": fb_in.comments},
        )
        db.add(audit)
        db.commit()
        db.refresh(fb)

        return FeedbackResponse.model_validate(fb)

    def get_analytics(self, db: Session, hotel_id: int) -> FeedbackAnalyticsResponse:
        """Compute model acceptance rate and post-stay revenue outcome metrics."""
        feedbacks = (
            db.query(Feedback)
            .join(PriceRecommendations, Feedback.recommendation_id == PriceRecommendations.recommendation_id)
            .filter(PriceRecommendations.hotel_id == hotel_id)
            .all()
        )

        total_count = len(feedbacks)
        if total_count == 0:
            return FeedbackAnalyticsResponse(
                hotel_id=hotel_id,
                total_recommendations_count=0,
                accepted_count=0,
                rejected_count=0,
                acceptance_rate_pct=100.0,
                average_actual_occupancy_pct=0.0,
                average_actual_adr=0.0,
                comments_summary=[],
            )

        accepted_list = [f for f in feedbacks if f.accepted]
        rejected_list = [f for f in feedbacks if not f.accepted]

        acc_pct = round((len(accepted_list) / total_count) * 100.0, 1)

        actual_occs = [
            f.actual_result["actual_occupancy"]
            for f in feedbacks
            if f.actual_result and "actual_occupancy" in f.actual_result
        ]
        actual_adrs = [
            f.actual_result["actual_adr"]
            for f in feedbacks
            if f.actual_result and "actual_adr" in f.actual_result
        ]

        avg_occ = round(sum(actual_occs) / len(actual_occs), 1) if actual_occs else 0.0
        avg_adr = round(sum(actual_adrs) / len(actual_adrs), 2) if actual_adrs else 0.0

        comments = [f.comments for f in feedbacks if f.comments]

        return FeedbackAnalyticsResponse(
            hotel_id=hotel_id,
            total_recommendations_count=total_count,
            accepted_count=len(accepted_list),
            rejected_count=len(rejected_list),
            acceptance_rate_pct=acc_pct,
            average_actual_occupancy_pct=avg_occ,
            average_actual_adr=avg_adr,
            comments_summary=comments[:10],
        )


feedback_service = FeedbackService()
