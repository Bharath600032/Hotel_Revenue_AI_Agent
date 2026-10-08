from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class DeveloperAPIKey(Base):
    __tablename__ = "developer_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    api_key_prefix = Column(String(50), nullable=False)
    api_key_hash = Column(String(255), nullable=False, unique=True, index=True)
    scopes = Column(JSON, default=list) # e.g. ["pricing:read", "pricing:write", "reports:read", "webhooks:manage"]
    status = Column(String(50), default="active") # active, revoked, expired
    rate_limit_per_min = Column(Integer, default=120)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hotel = relationship("Hotel", backref="api_keys")

class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    endpoint_url = Column(String(500), nullable=False)
    secret_key = Column(String(255), nullable=False)
    events = Column(JSON, default=list) # e.g. ["price.updated", "anomalies.detected", "report.generated", "swarm.consensus"]
    status = Column(String(50), default="active") # active, paused, disabled
    description = Column(String(255), nullable=True)
    failure_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hotel = relationship("Hotel", backref="webhook_subscriptions")
    event_logs = relationship("WebhookEventLog", backref="subscription", cascade="all, delete-orphan")

class WebhookEventLog(Base):
    __tablename__ = "webhook_event_logs"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    response_status_code = Column(Integer, default=200)
    response_body = Column(Text, nullable=True)
    delivered_at = Column(DateTime, default=datetime.utcnow)
    execution_time_ms = Column(Float, default=45.2)

    # Relationships
    hotel = relationship("Hotel", backref="webhook_logs")
