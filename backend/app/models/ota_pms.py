from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class PMSConnector(Base):
    __tablename__ = "pms_connectors"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    pms_provider = Column(String(100), nullable=False, default="OPERA_CLOUD") # OPERA_CLOUD, STAAH, EZEE_ABSOLUTE, HOTELOGIX, PROLOGIC, RMS_CLOUD
    connection_status = Column(String(50), default="CONNECTED") # CONNECTED, SYNCING, DISCONNECTED, ERROR
    api_endpoint = Column(String(500), nullable=False)
    sync_frequency_mins = Column(Integer, default=5)
    last_sync_at = Column(DateTime, nullable=True)
    auto_rate_push = Column(Boolean, default=True)
    auto_reservation_pull = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hotel = relationship("Hotel", backref="pms_connector")

class OTAChannelConnection(Base):
    __tablename__ = "ota_channel_connections"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    channel_name = Column(String(100), nullable=False) # Booking.com, MakeMyTrip, Goibibo, Agoda, Expedia, Airbnb
    channel_code = Column(String(20), nullable=False) # BCOM, MMT, GOI, AGD, EXP, ARB
    connection_status = Column(String(50), default="ACTIVE") # ACTIVE, PAUSED, ERROR
    commission_pct = Column(Float, default=18.0)
    rate_parity_status = Column(String(50), default="PARITY_OK") # PARITY_OK, UNDERCUT_DETECTED, BREACH_WARNING
    mapped_room_count = Column(Integer, default=6)
    last_pushed_rate_inr = Column(Float, default=8500.0)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hotel = relationship("Hotel", backref="ota_channels")

class PMSChannelSyncLog(Base):
    __tablename__ = "pms_channel_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    sync_type = Column(String(50), nullable=False) # RATE_PUSH, RESERVATION_PULL, INVENTORY_SYNC, PARITY_CHECK
    target_channel = Column(String(100), nullable=False) # OPERA_CLOUD, BOOKING_COM, ALL_CHANNELS
    status = Column(String(50), default="SUCCESS") # SUCCESS, PARTIAL_SUCCESS, FAILED
    records_processed = Column(Integer, default=1)
    details_json = Column(JSON, nullable=False)
    execution_time_ms = Column(Float, default=64.2)
    synced_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hotel = relationship("Hotel", backref="pms_sync_logs")
