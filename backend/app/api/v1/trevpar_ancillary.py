"""
REST API router for Total Revenue Management (TRevPAR) & Non-Room Revenue AI optimization.
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.trevpar_ancillary import (
    TRevPARSummaryResponse,
    AncillaryPackageRecommendationResponse,
    AncillaryRevenueCreate,
    AncillaryRevenueResponse,
)
from app.services.trevpar_service import trevpar_service
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels", tags=["TRevPAR & Non-Room Revenue AI"])


@router.get("/{hotel_id}/trevpar/summary", response_model=TRevPARSummaryResponse)
async def get_trevpar_summary(
    hotel_id: int,
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """
    Fetch Total Revenue Per Available Room (TRevPAR), RevPAR, NRevPAR, RevPOR,
    and non-room revenue stream breakdown across F&B, Spa, Banquets, Parking, Laundry.
    """
    verify_hotel_access(hotel_id, current_user, db)
    if not start_date:
        start_date = (date.today() - date.resolution * 7).strftime("%Y-%m-%d")
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    return trevpar_service.calculate_trevpar_summary(
        db, hotel_id=hotel_id, start_date=start_date, end_date=end_date
    )


@router.get("/{hotel_id}/trevpar/packages", response_model=List[AncillaryPackageRecommendationResponse])
async def get_ancillary_packages(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """
    Fetch AI dynamic non-room revenue upsell packages & bundle yield optimization recommendations.
    """
    verify_hotel_access(hotel_id, current_user, db)
    return trevpar_service.generate_ancillary_packages(db, hotel_id=hotel_id)


@router.post("/{hotel_id}/trevpar/ancillary-entry", response_model=AncillaryRevenueResponse, status_code=status.HTTP_201_CREATED)
async def record_ancillary_entry(
    hotel_id: int,
    payload: AncillaryRevenueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """
    Record manual or POS integrated non-room ancillary revenue entry for F&B, Spa, Banquets, Parking, etc.
    """
    verify_hotel_access(hotel_id, current_user, db)
    return trevpar_service.record_ancillary_entry(db, hotel_id=hotel_id, req=payload)
