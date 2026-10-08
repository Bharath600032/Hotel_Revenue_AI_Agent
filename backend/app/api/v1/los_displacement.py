"""
REST API endpoints for Length of Stay (LOS) Rules & Corporate Group Displacement Analysis.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.los_displacement import (
    GroupDisplacementRequest,
    GroupDisplacementResponse,
    LOSRuleResponse,
    LOSRuleUpdate,
)
from app.services.los_displacement_service import los_displacement_service
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels", tags=["LOS & Group Displacement AI"])


@router.post("/{hotel_id}/group-displacement/evaluate", response_model=GroupDisplacementResponse, status_code=status.HTTP_200_OK)
async def evaluate_group_displacement(
    hotel_id: int,
    payload: GroupDisplacementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst"])),
):
    """
    Evaluate financial impact of a corporate group request vs displaced transient revenue.
    """
    verify_hotel_access(hotel_id, current_user, db)
    return los_displacement_service.evaluate_group_displacement(
        db, hotel_id=hotel_id, req=payload, user_id=current_user.user_id
    )


@router.get("/{hotel_id}/group-displacement/logs", response_model=List[GroupDisplacementResponse])
async def get_group_displacement_logs(
    hotel_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve history of group displacement evaluation logs."""
    verify_hotel_access(hotel_id, current_user, db)
    return los_displacement_service.get_group_displacement_logs(db, hotel_id=hotel_id, limit=limit)


@router.get("/{hotel_id}/los-rules", response_model=List[LOSRuleResponse])
async def get_los_rules(
    hotel_id: int,
    start_date: Optional[str] = Query(None, description="Start stay date YYYY-MM-DD"),
    days: int = Query(14, ge=1, le=60),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Fetch Minimum Length of Stay (MLOS), CTA, CTD rules for stay dates."""
    verify_hotel_access(hotel_id, current_user, db)
    if not start_date:
        from datetime import date
        start_date = date.today().strftime("%Y-%m-%d")
    return los_displacement_service.get_los_rules(db, hotel_id=hotel_id, start_date=start_date, days=days)


@router.put("/{hotel_id}/los-rules/{stay_date}", response_model=LOSRuleResponse)
async def update_los_rule(
    hotel_id: int,
    stay_date: str,
    payload: LOSRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Update or override Length of Stay (MLOS) & CTA restrictions for a stay date."""
    verify_hotel_access(hotel_id, current_user, db)
    return los_displacement_service.update_los_rule(
        db, hotel_id=hotel_id, stay_date=stay_date, req=payload, user_id=current_user.user_id
    )
