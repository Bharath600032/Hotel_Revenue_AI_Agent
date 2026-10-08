"""
API routes for Option 4: Automated Multi-Channel Alerts & Notifications.
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alerts import (
    AlertRuleResponse,
    AlertRuleUpdate,
    AlertDispatchPayload,
    AlertLogResponse,
    AlertAcknowledgeRequest,
    ChannelTestRequest,
    ChannelTestResponse,
)
from app.services.alert_service import alert_service
from app.api.deps import verify_hotel_access, get_current_user
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger("app.api.v1.alerts")

router = APIRouter(prefix="/hotels/{hotel_id}/alerts", tags=["Alerts & Notifications"])


@router.get("", response_model=List[AlertLogResponse])
def get_alerts_log(
    hotel_id: int,
    status_filter: Optional[str] = Query("ALL", alias="status"),
    channel_filter: Optional[str] = Query("ALL", alias="channel"),
    severity_filter: Optional[str] = Query("ALL", alias="severity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve multi-channel alert dispatch logs with optional filters."""
    verify_hotel_access(hotel_id, current_user, db)
    return alert_service.get_alert_logs(
        db,
        hotel_id,
        status_filter=status_filter,
        channel_filter=channel_filter,
        severity_filter=severity_filter,
    )


@router.post("/dispatch", response_model=AlertLogResponse)
def dispatch_alert_notification(
    hotel_id: int,
    payload: AlertDispatchPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually or agent-trigger dispatch of a multi-channel alert."""
    verify_hotel_access(hotel_id, current_user, db)
    if payload.hotel_id != hotel_id:
        payload.hotel_id = hotel_id
    return alert_service.dispatch_alert(db, payload)


@router.post("/{log_id}/acknowledge", response_model=AlertLogResponse)
def acknowledge_alert_notification(
    hotel_id: int,
    log_id: int,
    body: AlertAcknowledgeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert log notification as ACKNOWLEDGED."""
    verify_hotel_access(hotel_id, current_user, db)
    try:
        return alert_service.acknowledge_alert(db, hotel_id, log_id, body.acknowledged_by)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/rules", response_model=List[AlertRuleResponse])
def get_alert_rules(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve multi-channel alert notification rules configuration matrix."""
    verify_hotel_access(hotel_id, current_user, db)
    return alert_service.get_alert_rules(db, hotel_id)


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
def update_alert_rule(
    hotel_id: int,
    rule_id: int,
    payload: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update threshold or channel toggles for an alert rule."""
    verify_hotel_access(hotel_id, current_user, db)
    try:
        return alert_service.update_alert_rule(db, hotel_id, rule_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/test-dispatch", response_model=ChannelTestResponse)
def test_channel_dispatch(
    hotel_id: int,
    request: ChannelTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simulate real-time multi-channel delivery test dispatch (Email, WhatsApp, Slack, In-App)."""
    verify_hotel_access(hotel_id, current_user, db)
    return alert_service.test_channel_dispatch(db, hotel_id, request)
