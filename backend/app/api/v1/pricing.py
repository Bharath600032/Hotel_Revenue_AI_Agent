"""
Pricing Engine REST API endpoints.
"""
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.pricing import (
    PriceRecommendationResponse,
    PriceRecommendationRequest,
    BatchRecommendationRequest,
    BatchRecommendationResponse,
)
from app.pricing.engine import pricing_engine
from app.models.ai import PriceRecommendations
from app.models.hotel import RoomType
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}/pricing", tags=["Pricing Engine"])


@router.post("/recommend", response_model=PriceRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def recommend_price(
    hotel_id: int,
    payload: PriceRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Analyst"])),
):
    """Generate dynamic room rate recommendation for a room type and stay date."""
    verify_hotel_access(hotel_id, current_user)
    return pricing_engine.calculate_recommendation(
        db, hotel_id=hotel_id, room_type_id=payload.room_type_id, stay_date=payload.stay_date
    )


@router.post("/recommend-batch", response_model=BatchRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def recommend_price_batch(
    hotel_id: int,
    payload: BatchRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager"])),
):
    """Generate dynamic rate recommendations for upcoming stay horizon (e.g. 30 to 365 days)."""
    verify_hotel_access(hotel_id, current_user)

    if payload.room_type_id:
        room_types = [db.query(RoomType).filter(RoomType.room_type_id == payload.room_type_id).first()]
    else:
        room_types = db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()

    recommendations: List[PriceRecommendationResponse] = []
    for rt in room_types:
        if not rt:
            continue
        for i in range(payload.days_count):
            target_dt = payload.start_date + timedelta(days=i)
            rec = pricing_engine.calculate_recommendation(
                db, hotel_id=hotel_id, room_type_id=rt.room_type_id, stay_date=target_dt
            )
            recommendations.append(rec)

    return BatchRecommendationResponse(
        hotel_id=hotel_id,
        total_recommendations=len(recommendations),
        recommendations=recommendations,
    )


@router.get("/recommendations", response_model=List[PriceRecommendationResponse])
async def list_recommendations(
    hotel_id: int,
    room_type_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve persisted price recommendations with optional status and stay date filters."""
    verify_hotel_access(hotel_id, current_user)
    query = db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == hotel_id)
    if room_type_id:
        query = query.filter(PriceRecommendations.room_type_id == room_type_id)
    if start_date:
        query = query.filter(PriceRecommendations.stay_date >= start_date)
    if end_date:
        query = query.filter(PriceRecommendations.stay_date <= end_date)
    if status:
        query = query.filter(PriceRecommendations.status == status)

    return query.order_by(PriceRecommendations.stay_date).all()


@router.post("/autonomous-cycle", status_code=status.HTTP_200_OK)
async def run_autonomous_cycle(
    hotel_id: int,
    horizon_days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager"])),
):
    """Run the 5-Stage Controlled Autonomous Pricing Cycle for the specified stay date horizon."""
    verify_hotel_access(hotel_id, current_user)
    return pricing_engine.run_autonomous_pricing_cycle(db, hotel_id=hotel_id, horizon_days=horizon_days)


@router.get("/pipeline-status", status_code=status.HTTP_200_OK)
async def get_pipeline_status(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst"])),
):
    """Get real-time metrics across all 5 pricing pipeline stages."""
    verify_hotel_access(hotel_id, current_user)
    return pricing_engine.get_pipeline_status(db, hotel_id=hotel_id)


@router.post("/publish/{recommendation_id}")
async def publish_recommendation(
    hotel_id: int,
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Stage 4: Explicitly publish a recommended rate to RoomInventory and live booking engine."""
    from app.services.approval_service import approval_service
    verify_hotel_access(hotel_id, current_user)
    return approval_service.publish_recommendation(db, recommendation_id=recommendation_id, user_id=current_user.user_id)

