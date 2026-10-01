"""
Audit logs ORM model for capturing all database modifications and security operations.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, JSON, ForeignKey, Index, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AuditLogs(Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    hotel_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    old_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_audit_action_entity", "action", "entity_type"),
    )
