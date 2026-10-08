from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PMSConnectorConfigureRequest(BaseModel):
    pms_provider: str = Field(..., example="OPERA_CLOUD")
    api_endpoint: str = Field(..., example="https://opera-cloud.oracle.com/api/v1/hotels/HAR-IND-01")
    sync_frequency_mins: int = Field(default=5, ge=1, le=60)
    auto_rate_push: bool = Field(default=True)
    auto_reservation_pull: bool = Field(default=True)

class PMSConnectorResponse(BaseModel):
    id: int
    hotel_id: int
    pms_provider: str
    connection_status: str
    api_endpoint: str
    sync_frequency_mins: int
    last_sync_at: Optional[datetime]
    auto_rate_push: bool
    auto_reservation_pull: bool
    created_at: datetime

    class Config:
        from_attributes = True

class OTAChannelResponse(BaseModel):
    id: int
    hotel_id: int
    channel_name: str
    channel_code: str
    connection_status: str
    commission_pct: float
    rate_parity_status: str
    mapped_room_count: int
    last_pushed_rate_inr: float
    last_sync_at: Optional[datetime]

    class Config:
        from_attributes = True

class OTAChannelCreateRequest(BaseModel):
    channel_name: str = Field(..., example="TripAdvisor")
    channel_code: str = Field(..., example="TA")
    commission_pct: float = Field(..., ge=0.0, le=50.0, example=15.0)
    mapped_room_count: Optional[int] = Field(default=8, ge=1)
    last_pushed_rate_inr: Optional[float] = Field(default=9500.0, gt=0.0)

class OTAChannelUpdateRequest(BaseModel):
    channel_name: Optional[str] = Field(None, example="Booking.com Premier")
    commission_pct: Optional[float] = Field(None, ge=0.0, le=50.0, example=17.5)
    connection_status: Optional[str] = Field(None, example="ACTIVE")
    rate_parity_status: Optional[str] = Field(None, example="PARITY_OK")
    mapped_room_count: Optional[int] = Field(None, ge=1)
    last_pushed_rate_inr: Optional[float] = Field(None, gt=0.0)


class RatePushRequest(BaseModel):
    target_channels: Optional[List[str]] = Field(default=["OPERA_CLOUD", "BOOKING_COM", "MAKEMYTRIP", "AGODA", "GOIBIBO", "EXPEDIA"])
    room_type: str = Field(..., example="Deluxe Ocean Suite")
    recommended_rate_inr: float = Field(..., gt=0.0, example=10500.0)
    override_reason: Optional[str] = Field(None, example="AI Dynamic Demand Surge Strategy")

class RatePushResponse(BaseModel):
    sync_id: int
    hotel_id: int
    status: str
    target_channels: List[str]
    pushed_rate_inr: float
    parity_check: str
    records_updated: int
    execution_time_ms: float
    synced_at: datetime

class PMSReservationPullResponse(BaseModel):
    sync_id: int
    hotel_id: int
    pms_provider: str
    new_reservations_count: int
    total_revenue_inr: float
    status: str
    synced_at: datetime

class SyncLogResponse(BaseModel):
    id: int
    hotel_id: int
    sync_type: str
    target_channel: str
    status: str
    records_processed: int
    details_json: Dict[str, Any]
    execution_time_ms: float
    synced_at: datetime

    class Config:
        from_attributes = True
