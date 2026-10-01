"""
Hotel Revenue Analytics REST API endpoints.
"""
from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.revenue import (
    RevenueSummary,
    PickupPace,
    ChannelContribution,
    DayOfWeekPerformance,
)
from app.services.revenue_calculator import revenue_calculator
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}/analytics", tags=["Revenue Analytics"])


@router.get("/metrics", response_model=RevenueSummary)
async def get_revenue_summary(
    hotel_id: int,
    start_date: date = Query(..., description="Start stay date"),
    end_date: date = Query(..., description="End stay date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Calculate aggregate revenue KPIs (Occupancy, ADR, RevPAR, TRevPAR, Cancellation Rate)."""
    verify_hotel_access(hotel_id, current_user)
    return revenue_calculator.calculate_period_summary(
        db, hotel_id=hotel_id, start_date=start_date, end_date=end_date
    )


@router.get("/pickup", response_model=PickupPace)
async def get_pickup_pace(
    hotel_id: int,
    stay_date: date = Query(..., description="Target stay date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve 1d, 3d, 7d, 14d, 30d pickup pace for target stay date."""
    verify_hotel_access(hotel_id, current_user)
    return revenue_calculator.calculate_pickup_pace(db, hotel_id=hotel_id, stay_date=stay_date)


@router.get("/channels", response_model=List[ChannelContribution])
async def get_channel_performance(
    hotel_id: int,
    start_date: date = Query(..., description="Start stay date"),
    end_date: date = Query(..., description="End stay date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve channel revenue mix and percentage contribution."""
    verify_hotel_access(hotel_id, current_user)
    return revenue_calculator.calculate_channel_performance(
        db, hotel_id=hotel_id, start_date=start_date, end_date=end_date
    )


@router.get("/day-of-week", response_model=List[DayOfWeekPerformance])
async def get_day_of_week_performance(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve day-of-week demand performance multipliers."""
    verify_hotel_access(hotel_id, current_user)
    return revenue_calculator.calculate_day_of_week_performance(db, hotel_id=hotel_id)
