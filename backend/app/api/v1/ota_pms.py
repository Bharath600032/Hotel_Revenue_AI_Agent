from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.deps import get_current_user, verify_hotel_access
from app.models.user import User
from app.schemas.ota_pms import (
    PMSConnectorConfigureRequest,
    PMSConnectorResponse,
    OTAChannelResponse,
    RatePushRequest,
    RatePushResponse,
    PMSReservationPullResponse,
    SyncLogResponse,
)
from app.services.ota_pms_service import OTAPMSService

router = APIRouter(prefix="/channels", tags=["OTA & PMS Channel Connectors"])

@router.get("/pms-connector", response_model=PMSConnectorResponse)
def get_pms_connector(
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve active PMS integration connector status."""
    verify_hotel_access(hotel_id, current_user, db)
    return OTAPMSService.get_pms_connector(hotel_id, db)

@router.get("/ota-channels", response_model=List[OTAChannelResponse])
def get_ota_channels(
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all connected OTA channel mappings, rate parity statuses, and commissions."""
    verify_hotel_access(hotel_id, current_user, db)
    return OTAPMSService.get_ota_channels(hotel_id, db)

@router.post("/push-rates", response_model=RatePushResponse)
def push_two_way_rates(
    request: RatePushRequest,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger immediate 2-way rate push to Opera Cloud PMS and all connected OTAs (Booking.com, MMT, Agoda)."""
    verify_hotel_access(hotel_id, current_user, db)
    log = OTAPMSService.push_rates(
        hotel_id=hotel_id,
        room_type=request.room_type,
        recommended_rate_inr=request.recommended_rate_inr,
        target_channels=request.target_channels,
        override_reason=request.override_reason,
        db=db,
    )
    return RatePushResponse(
        sync_id=log.id,
        hotel_id=log.hotel_id,
        status=log.status,
        target_channels=request.target_channels or ["ALL_CHANNELS"],
        pushed_rate_inr=request.recommended_rate_inr,
        parity_check="COMPLIANT",
        records_updated=log.records_processed,
        execution_time_ms=log.execution_time_ms,
        synced_at=log.synced_at,
    )

@router.post("/pull-reservations", response_model=PMSReservationPullResponse)
def pull_pms_reservations(
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger live reservation sync from PMS to update real-time booking inventory snapshot."""
    verify_hotel_access(hotel_id, current_user, db)
    log = OTAPMSService.pull_reservations(hotel_id, db)
    return PMSReservationPullResponse(
        sync_id=log.id,
        hotel_id=log.hotel_id,
        pms_provider="OPERA_CLOUD",
        new_reservations_count=log.records_processed,
        total_revenue_inr=log.details_json.get("total_revenue_inr", 0.0),
        status=log.status,
        synced_at=log.synced_at,
    )

@router.get("/sync-logs", response_model=List[SyncLogResponse])
def get_sync_logs(
    hotel_id: int = Query(..., description="ID of the hotel"),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve 2-way PMS & OTA rate push and reservation pull sync audit logs."""
    verify_hotel_access(hotel_id, current_user, db)
    return OTAPMSService.get_sync_logs(hotel_id, db, limit=limit)
