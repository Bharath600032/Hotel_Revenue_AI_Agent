"""
SQLAlchemy ORM models for Option 4: Automated Multi-Channel Alerts & Notifications.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class AlertNotificationRule(Base):
    """Configuration matrix for automated multi-channel notification rules."""
    __tablename__ = "alert_notification_rules"

    rule_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id", ondelete="CASCADE"), nullable=False, index=True)

    alert_type = Column(String(50), nullable=False, index=True)  # COMPETITOR_UNDERCUT, PACE_SURGE, DISPLACEMENT_THRESHOLD, TREVPAR_BREACH, HIGH_DEMAND_EVENT
    rule_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    threshold_value = Column(Float, nullable=False, default=10.0)  # e.g., 10% drop or ₹500 change
    severity = Column(String(20), nullable=False, default="WARNING")  # CRITICAL, WARNING, INFO

    is_enabled = Column(Boolean, nullable=False, default=True)
    notify_email = Column(Boolean, nullable=False, default=True)
    notify_whatsapp = Column(Boolean, nullable=False, default=True)
    notify_slack = Column(Boolean, nullable=False, default=True)
    notify_in_app = Column(Boolean, nullable=False, default=True)

    recipients = Column(String(255), nullable=True, default="revenue@hotel.com, gm@hotel.com")
    slack_webhook_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    hotel = relationship("Hotel", backref="alert_rules")


class AlertNotificationLog(Base):
    """Log of dispatched multi-channel alerts and acknowledgment history."""
    __tablename__ = "alert_notification_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey("alert_notification_rules.rule_id", ondelete="SET NULL"), nullable=True)

    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="WARNING")  # CRITICAL, WARNING, INFO
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String(30), nullable=False, default="MULTI_CHANNEL")  # EMAIL, WHATSAPP, SLACK, IN_APP, MULTI_CHANNEL
    status = Column(String(20), nullable=False, default="DISPATCHED")  # DISPATCHED, DELIVERED, FAILED, ACKNOWLEDGED
    recipient = Column(String(255), nullable=True)

    metadata_json = Column(JSON, nullable=True)  # Context data: competitor price, date range, breach amount, etc.

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(100), nullable=True)

    hotel = relationship("Hotel", backref="alert_logs")
    rule = relationship("AlertNotificationRule", backref="logs")
