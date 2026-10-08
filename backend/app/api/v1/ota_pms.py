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
    OTAChannelCreateRequest,
    OTAChannelUpdateRequest,
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

@router.post("/ota-channels", response_model=OTAChannelResponse)
def create_ota_channel(
    request: OTAChannelCreateRequest,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new OTA distribution channel connection."""
    verify_hotel_access(hotel_id, current_user, db)
    return OTAPMSService.create_ota_channel(
        hotel_id=hotel_id,
        channel_name=request.channel_name,
        channel_code=request.channel_code,
        commission_pct=request.commission_pct,
        mapped_room_count=request.mapped_room_count,
        last_pushed_rate_inr=request.last_pushed_rate_inr,
        db=db,
    )

@router.put("/ota-channels/{channel_id}", response_model=OTAChannelResponse)
def update_ota_channel(
    channel_id: int,
    request: OTAChannelUpdateRequest,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update OTA channel details, including editable commission percentage and parity status."""
    verify_hotel_access(hotel_id, current_user, db)
    updated = OTAPMSService.update_ota_channel(
        hotel_id=hotel_id,
        channel_id=channel_id,
        update_data=request.model_dump(exclude_unset=True),
        db=db,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="OTA channel not found")
    return updated

@router.delete("/ota-channels/{channel_id}")
def delete_ota_channel(
    channel_id: int,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove/disconnect an OTA channel mapping."""
    verify_hotel_access(hotel_id, current_user, db)
    deleted = OTAPMSService.delete_ota_channel(hotel_id, channel_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="OTA channel not found")
    return {"message": "OTA channel deleted successfully", "channel_id": channel_id}

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
