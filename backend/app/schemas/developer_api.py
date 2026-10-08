from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# API Key Schemas
class APIKeyCreateRequest(BaseModel):
    name: str = Field(..., example="PMS Channel Sync Engine")
    scopes: List[str] = Field(default=["pricing:read", "pricing:write", "reports:read", "webhooks:manage"])
    expires_in_days: Optional[int] = Field(default=90, description="Expiration in days (null for never)")

class APIKeyCreateResponse(BaseModel):
    id: int
    hotel_id: int
    name: str
    api_key_raw: str  # Plaintext key shown ONLY once upon generation
    api_key_prefix: str
    scopes: List[str]
    status: str
    created_at: datetime
    expires_at: Optional[datetime]

class APIKeyResponse(BaseModel):
    id: int
    hotel_id: int
    name: str
    api_key_prefix: str
    scopes: List[str]
    status: str
    rate_limit_per_min: int
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# Webhook Schemas
class WebhookCreateRequest(BaseModel):
    endpoint_url: str = Field(..., example="https://api.myhotelpms.com/webhooks/har-events")
    events: List[str] = Field(..., example=["price.updated", "anomalies.detected", "report.generated", "swarm.consensus"])
    description: Optional[str] = Field(None, example="Main PMS Webhook Receiver")

class WebhookSubscriptionResponse(BaseModel):
    id: int
    hotel_id: int
    endpoint_url: str
    secret_key: str
    events: List[str]
    status: str
    description: Optional[str]
    failure_count: int
    last_triggered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class WebhookDispatchTestRequest(BaseModel):
    subscription_id: int
    event_type: Optional[str] = "price.updated"

class WebhookEventLogResponse(BaseModel):
    id: int
    hotel_id: int
    subscription_id: int
    event_type: str
    payload: Dict[str, Any]
    response_status_code: int
    response_body: Optional[str]
    delivered_at: datetime
    execution_time_ms: float

    class Config:
        from_attributes = True
