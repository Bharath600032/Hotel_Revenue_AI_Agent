"""
Human Approval Workflow REST API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.approval import ApprovalResponse, OverrideRequest, RejectRequest
from app.schemas.pricing import PriceRecommendationResponse
from app.services.approval_service import approval_service
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}/approvals", tags=["Human Approval Workflow"])


@router.get("/pending", response_model=List[PriceRecommendationResponse])
async def list_pending_approvals(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Retrieve queue of price recommendations pending human approval."""
    verify_hotel_access(hotel_id, current_user)
    return approval_service.get_pending_queue(db, hotel_id=hotel_id)


@router.post("/{recommendation_id}/approve", response_model=ApprovalResponse)
async def approve_recommendation(
    hotel_id: int,
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Approve a price recommendation for production deployment."""
    verify_hotel_access(hotel_id, current_user)
    return approval_service.approve_recommendation(
        db, recommendation_id=recommendation_id, user_id=current_user.user_id
    )


@router.post("/{recommendation_id}/override", response_model=ApprovalResponse)
async def override_recommendation(
    hotel_id: int,
    recommendation_id: int,
    payload: OverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Override a price recommendation with custom manager rate."""
    verify_hotel_access(hotel_id, current_user)
    return approval_service.override_recommendation(
        db,
        recommendation_id=recommendation_id,
        user_id=current_user.user_id,
        override_rate=payload.override_rate,
        reason=payload.reason,
    )


@router.post("/{recommendation_id}/reject", response_model=ApprovalResponse)
async def reject_recommendation(
    hotel_id: int,
    recommendation_id: int,
    payload: RejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Reject a price recommendation."""
    verify_hotel_access(hotel_id, current_user)
    return approval_service.reject_recommendation(
        db,
        recommendation_id=recommendation_id,
        user_id=current_user.user_id,
        reason=payload.reason,
    )
