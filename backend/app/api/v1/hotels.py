"""
Hotels, Room Types, and Rate Plans REST API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.hotel import HotelResponse, HotelCreate, HotelUpdate
from app.schemas.room_type import RoomTypeResponse, RoomTypeCreate, RoomTypeUpdate
from app.schemas.rate_plan import RatePlanResponse, RatePlanCreate, RatePlanUpdate
from app.services.hotel_service import hotel_service
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels", tags=["Hotels & Master Data"])


# --- Hotels Endpoints ---
@router.get("", response_model=List[HotelResponse])
async def list_hotels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    city: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve list of hotels accessible to current user."""
    return hotel_service.list_hotels(db, skip=skip, limit=limit, city=city, user=current_user)


@router.post("", response_model=HotelResponse, status_code=status.HTTP_201_CREATED)
async def create_hotel(
    payload: HotelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Create a new property master record."""
    return hotel_service.create_hotel(db, hotel_in=payload, user_id=current_user.user_id)


@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve details for a specific hotel by ID."""
    verify_hotel_access(hotel_id, current_user, db)
    return hotel_service.get_hotel(db, hotel_id=hotel_id)


@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(
    hotel_id: int,
    payload: HotelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Update hotel master profile."""
    verify_hotel_access(hotel_id, current_user, db)
    return hotel_service.update_hotel(db, hotel_id=hotel_id, hotel_in=payload, user_id=current_user.user_id)


@router.delete("/{hotel_id}", status_code=status.HTTP_200_OK)
async def delete_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Delete hotel property and all associated master records."""
    verify_hotel_access(hotel_id, current_user, db)
    hotel_service.delete_hotel(db, hotel_id=hotel_id, user_id=current_user.user_id)
    return {"status": "DELETED", "hotel_id": hotel_id}



# --- Room Types Endpoints ---
@router.get("/{hotel_id}/room-types", response_model=List[RoomTypeResponse])
async def list_room_types(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve room types for a specific hotel."""
    verify_hotel_access(hotel_id, current_user, db)
    return hotel_service.list_room_types(db, hotel_id=hotel_id)


@router.post("/{hotel_id}/room-types", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_room_type(
    hotel_id: int,
    payload: RoomTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Create a new room type for a hotel."""
    verify_hotel_access(hotel_id, current_user, db)
    return hotel_service.create_room_type(db, hotel_id=hotel_id, rt_in=payload, user_id=current_user.user_id)


# --- Rate Plans Endpoints ---
@router.get("/{hotel_id}/rate-plans", response_model=List[RatePlanResponse])
async def list_rate_plans(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve rate plans for a specific hotel."""
    verify_hotel_access(hotel_id, current_user, db)
    return hotel_service.list_rate_plans(db, hotel_id=hotel_id)


@router.post("/{hotel_id}/rate-plans", response_model=RatePlanResponse, status_code=status.HTTP_201_CREATED)
async def create_rate_plan(
    hotel_id: int,
    payload: RatePlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Create a new rate plan for a hotel."""
    verify_hotel_access(hotel_id, current_user, db)
    return hotel_service.create_rate_plan(db, hotel_id=hotel_id, rp_in=payload, user_id=current_user.user_id)
