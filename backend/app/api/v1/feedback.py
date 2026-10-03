"""
Feedback Loop & Model Analytics REST API endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackAnalyticsResponse
from app.services.feedback_service import feedback_service
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}/feedback", tags=["Feedback Loop & Model Analytics"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    hotel_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Submit revenue manager feedback and post-stay actual outcomes for rate recommendation."""
    verify_hotel_access(hotel_id, current_user, db)
    return feedback_service.submit_feedback(
        db, hotel_id=hotel_id, user_id=current_user.user_id, fb_in=payload
    )


@router.get("/analytics", response_model=FeedbackAnalyticsResponse)
async def get_feedback_analytics(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve model acceptance rate percentage and post-stay performance metrics."""
    verify_hotel_access(hotel_id, current_user, db)
    return feedback_service.get_analytics(db, hotel_id=hotel_id)
