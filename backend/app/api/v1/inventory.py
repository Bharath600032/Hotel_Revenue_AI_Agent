"""
Inventory, Reservations, and Data Import REST API endpoints.
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.inventory import RoomInventoryResponse, RoomInventoryCreate
from app.schemas.reservation import ReservationResponse, ReservationCreate
from app.schemas.import_schema import ImportPreview, ImportReport
from app.repositories.inventory_repository import inventory_repository
from app.repositories.reservation_repository import reservation_repository
from app.services.import_service import import_service
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}", tags=["Inventory, Reservations & Imports"])


# --- Inventory Endpoints ---
@router.get("/inventory", response_model=List[RoomInventoryResponse])
async def get_inventory(
    hotel_id: int,
    start_date: date = Query(..., description="Start stay date"),
    end_date: date = Query(..., description="End stay date"),
    room_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Query room inventory levels for stay date range."""
    verify_hotel_access(hotel_id, current_user)
    return inventory_repository.get_range(
        db, hotel_id=hotel_id, start_date=start_date, end_date=end_date, room_type_id=room_type_id
    )


@router.post("/inventory", response_model=RoomInventoryResponse)
async def update_inventory(
    hotel_id: int,
    payload: RoomInventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Upsert room inventory counts for a stay date."""
    verify_hotel_access(hotel_id, current_user)
    return inventory_repository.upsert(
        db,
        hotel_id=hotel_id,
        room_type_id=payload.room_type_id,
        stay_date=payload.stay_date,
        total_rooms=payload.total_rooms,
        available_rooms=payload.available_rooms,
        out_of_order=payload.out_of_order,
    )


# --- Reservations Endpoints ---
@router.get("/reservations", response_model=List[ReservationResponse])
async def list_reservations(
    hotel_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """List hotel reservations with filters and pagination."""
    verify_hotel_access(hotel_id, current_user)
    return reservation_repository.get_multi(
        db,
        hotel_id=hotel_id,
        skip=skip,
        limit=limit,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    hotel_id: int,
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Create a new single reservation."""
    verify_hotel_access(hotel_id, current_user)
    return reservation_repository.create(db, hotel_id=hotel_id, res_in=payload)


# --- Data Import Engine Endpoints ---
@router.post("/imports/preview", response_model=ImportPreview)
async def preview_import(
    hotel_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Dry-run preview and schema validation for CSV/Excel/JSON upload."""
    verify_hotel_access(hotel_id, current_user)
    contents = await file.read()
    return import_service.preview_import(db, hotel_id=hotel_id, file_bytes=contents, filename=file.filename)


@router.post("/imports/process", response_model=ImportReport)
async def process_import(
    hotel_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Execute batch data import with database transaction and row-level error log."""
    verify_hotel_access(hotel_id, current_user)
    contents = await file.read()
    return import_service.process_import(
        db, hotel_id=hotel_id, file_bytes=contents, filename=file.filename, user_id=current_user.user_id
    )
