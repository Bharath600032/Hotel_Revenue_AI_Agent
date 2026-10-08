"""
Pydantic schemas for Option 4: Automated Multi-Channel Alerts & Notifications.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class AlertRuleBase(BaseModel):
    alert_type: str = Field(..., description="COMPETITOR_UNDERCUT, PACE_SURGE, DISPLACEMENT_THRESHOLD, TREVPAR_BREACH, HIGH_DEMAND_EVENT")
    rule_name: str
    description: Optional[str] = None
    threshold_value: float = 10.0
    severity: str = "WARNING"
    is_enabled: bool = True
    notify_email: bool = True
    notify_whatsapp: bool = True
    notify_slack: bool = True
    notify_in_app: bool = True
    recipients: Optional[str] = "revenue@hotel.com, gm@hotel.com"
    slack_webhook_url: Optional[str] = None


class AlertRuleCreate(AlertRuleBase):
    hotel_id: int


class AlertRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    description: Optional[str] = None
    threshold_value: Optional[float] = None
    severity: Optional[str] = None
    is_enabled: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_whatsapp: Optional[bool] = None
    notify_slack: Optional[bool] = None
    notify_in_app: Optional[bool] = None
    recipients: Optional[str] = None
    slack_webhook_url: Optional[str] = None


class AlertRuleResponse(AlertRuleBase):
    rule_id: int
    hotel_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertDispatchPayload(BaseModel):
    hotel_id: int
    alert_type: str
    severity: str = "WARNING"
    title: str
    message: str
    channels: Optional[List[str]] = Field(default=["EMAIL", "WHATSAPP", "SLACK", "IN_APP"])
    recipient: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: str = "Revenue Manager"


class AlertLogResponse(BaseModel):
    log_id: int
    hotel_id: int
    rule_id: Optional[int] = None
    alert_type: str
    severity: str
    title: str
    message: str
    channel: str
    status: str
    recipient: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ChannelTestRequest(BaseModel):
    channel: str = Field(..., description="EMAIL, WHATSAPP, SLACK, IN_APP")
    target_destination: Optional[str] = None  # email address, phone number, or webhook URL
    sample_type: Optional[str] = "COMPETITOR_UNDERCUT"


class ChannelTestResponse(BaseModel):
    success: bool
    channel: str
    recipient: str
    formatted_payload: str
    dispatched_at: datetime
