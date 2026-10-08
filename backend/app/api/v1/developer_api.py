from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.deps import get_current_user, verify_hotel_access
from app.models.user import User
from app.schemas.developer_api import (
    APIKeyCreateRequest,
    APIKeyCreateResponse,
    APIKeyResponse,
    WebhookCreateRequest,
    WebhookSubscriptionResponse,
    WebhookDispatchTestRequest,
    WebhookEventLogResponse,
)
from app.services.developer_api_service import DeveloperAPIService

router = APIRouter(prefix="/developer", tags=["Developer & Webhooks"])

@router.get("/api-keys", response_model=List[APIKeyResponse])
def get_api_keys(
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all API keys configured for the hotel."""
    verify_hotel_access(hotel_id, current_user, db)
    return DeveloperAPIService.get_api_keys(hotel_id, db)

@router.post("/api-keys", response_model=APIKeyCreateResponse)
def create_api_key(
    request: APIKeyCreateRequest,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new developer API key. Note: The raw key is returned ONLY once."""
    verify_hotel_access(hotel_id, current_user, db)
    key_obj, raw_key = DeveloperAPIService.create_api_key(
        hotel_id=hotel_id,
        name=request.name,
        scopes=request.scopes,
        expires_in_days=request.expires_in_days,
        db=db,
    )
    return APIKeyCreateResponse(
        id=key_obj.id,
        hotel_id=key_obj.hotel_id,
        name=key_obj.name,
        api_key_raw=raw_key,
        api_key_prefix=key_obj.api_key_prefix,
        scopes=key_obj.scopes,
        status=key_obj.status,
        created_at=key_obj.created_at,
        expires_at=key_obj.expires_at,
    )

@router.delete("/api-keys/{key_id}", response_model=APIKeyResponse)
def revoke_api_key(
    key_id: int,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke an existing developer API key."""
    verify_hotel_access(hotel_id, current_user, db)
    revoked = DeveloperAPIService.revoke_api_key(hotel_id, key_id, db)
    if not revoked:
        raise HTTPException(status_code=404, detail="API Key not found")
    return revoked

@router.get("/webhooks", response_model=List[WebhookSubscriptionResponse])
def get_webhook_subscriptions(
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve active webhook subscriptions for the hotel."""
    verify_hotel_access(hotel_id, current_user, db)
    return DeveloperAPIService.get_webhooks(hotel_id, db)

@router.post("/webhooks", response_model=WebhookSubscriptionResponse)
def create_webhook_subscription(
    request: WebhookCreateRequest,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a new webhook endpoint URL to receive automated events."""
    verify_hotel_access(hotel_id, current_user, db)
    return DeveloperAPIService.create_webhook(
        hotel_id=hotel_id,
        endpoint_url=request.endpoint_url,
        events=request.events,
        description=request.description,
        db=db,
    )

@router.delete("/webhooks/{webhook_id}")
def delete_webhook_subscription(
    webhook_id: int,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a webhook subscription."""
    verify_hotel_access(hotel_id, current_user, db)
    success = DeveloperAPIService.delete_webhook(hotel_id, webhook_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook subscription not found")
    return {"message": "Webhook deleted successfully", "id": webhook_id}

@router.post("/webhooks/test-dispatch", response_model=WebhookEventLogResponse)
def test_dispatch_webhook(
    request: WebhookDispatchTestRequest,
    hotel_id: int = Query(..., description="ID of the hotel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dispatch a test webhook payload to simulate live integration delivery."""
    verify_hotel_access(hotel_id, current_user, db)
    try:
        return DeveloperAPIService.test_dispatch(
            hotel_id=hotel_id,
            subscription_id=request.subscription_id,
            event_type=request.event_type,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/webhooks/logs", response_model=List[WebhookEventLogResponse])
def get_webhook_logs(
    hotel_id: int = Query(..., description="ID of the hotel"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve live execution delivery logs for webhooks."""
    verify_hotel_access(hotel_id, current_user, db)
    return DeveloperAPIService.get_webhook_logs(hotel_id, db, limit=limit)
