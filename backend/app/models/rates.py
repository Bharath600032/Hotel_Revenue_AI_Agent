"""
Historical rates and Competitor pricing ORM models.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class HistoricalRates(Base):
    __tablename__ = "historical_rates"

    rate_log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    room_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("room_types.room_type_id"), nullable=False, index=True)
    stay_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    rate_plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("rate_plans.rate_plan_id"), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="PMS_LOG", nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_hist_rate_lookup", "hotel_id", "room_type_id", "stay_date"),
    )


class CompetitorHotels(Base):
    __tablename__ = "competitor_hotels"

    competitor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    competitor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    star_rating: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    # Relationships
    rates: Mapped[List["CompetitorRates"]] = relationship("CompetitorRates", back_populates="competitor", cascade="all, delete-orphan")


class CompetitorRates(Base):
    __tablename__ = "competitor_rates"

    competitor_rate_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competitor_id: Mapped[int] = mapped_column(Integer, ForeignKey("competitor_hotels.competitor_id"), nullable=False, index=True)
    stay_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    room_type: Mapped[str] = mapped_column(String(100), default="Deluxe", nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    availability: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meal_plan: Mapped[str] = mapped_column(String(50), default="EP", nullable=False)
    cancellation_policy: Mapped[str] = mapped_column(String(255), default="Standard", nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="OTA_FEED", nullable=False)
    ota_name: Mapped[Optional[str]] = mapped_column(String(100), default="Booking.com", nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    competitor: Mapped["CompetitorHotels"] = relationship("CompetitorHotels", back_populates="rates")

    __table_args__ = (
        Index("idx_comp_rate_lookup", "competitor_id", "stay_date"),
    )
