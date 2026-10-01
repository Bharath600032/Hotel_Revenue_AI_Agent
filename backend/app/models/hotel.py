"""
Hotel master data ORM models: Hotel, RoomType, RatePlan.
"""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Hotel(Base):
    __tablename__ = "hotels"

    hotel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hotel_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_rooms: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    min_price_floor: Mapped[float] = mapped_column(Float, default=3000.0, nullable=False)
    max_price_ceiling: Mapped[float] = mapped_column(Float, default=30000.0, nullable=False)
    max_daily_price_change_pct: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)
    require_approval_above_change_pct: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    automation_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    star_rating: Mapped[float] = mapped_column(Float, default=4.5, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    # Relationships
    room_types: Mapped[List["RoomType"]] = relationship("RoomType", back_populates="hotel", cascade="all, delete-orphan")
    rate_plans: Mapped[List["RatePlan"]] = relationship("RatePlan", back_populates="hotel", cascade="all, delete-orphan")


class RoomType(Base):
    __tablename__ = "room_types"

    room_type_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    room_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    room_type_name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_occupancy: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_inventory: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="room_types")

    __table_args__ = (
        CheckConstraint("base_price > 0", name="chk_room_base_price_positive"),
    )


class RatePlan(Base):
    __tablename__ = "rate_plans"

    rate_plan_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    rate_plan_code: Mapped[str] = mapped_column(String(50), nullable=False)
    rate_plan_name: Mapped[str] = mapped_column(String(100), nullable=False)
    meal_plan: Mapped[str] = mapped_column(String(50), default="EP", nullable=False)  # EP, CP, MAP, AP
    cancellation_policy: Mapped[str] = mapped_column(String(255), default="24_HOURS_FREE", nullable=False)
    refundable: Mapped[bool] = mapped_column(default=True, nullable=False)
    multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="rate_plans")
