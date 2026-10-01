"""
Inventory, Reservation, and Daily Booking Snapshot ORM models.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class RoomInventory(Base):
    __tablename__ = "room_inventory"

    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    room_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("room_types.room_type_id"), nullable=False, index=True)
    stay_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_inventory: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    sold_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_rate: Mapped[float] = mapped_column(Float, default=5000.0, nullable=False)
    total_rooms: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    available_rooms: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    out_of_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sellable_rooms: Mapped[int] = mapped_column(Integer, default=25, nullable=False)

    __table_args__ = (
        Index("idx_inventory_hotel_stay", "hotel_id", "stay_date"),
        Index("idx_inventory_room_stay", "room_type_id", "stay_date"),
    )


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    booking_reference: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    reservation_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    room_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("room_types.room_type_id"), nullable=False)
    rate_plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("rate_plans.rate_plan_id"), nullable=False)
    guest_name: Mapped[str] = mapped_column(String(255), default="Guest", nullable=False)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    checkout_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    room_nights: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    rooms_booked: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    adults: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    children: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="Direct", index=True, nullable=False)
    booking_channel: Mapped[str] = mapped_column(String(50), default="Direct", index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Confirmed", index=True, nullable=False)
    reservation_status: Mapped[str] = mapped_column(String(30), default="CONFIRMED", index=True, nullable=False)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    room_rate: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Index("idx_res_hotel_checkin", "hotel_id", "checkin_date"),
        Index("idx_res_booking_date", "hotel_id", "booking_date"),
    )


class DailyBookingSnapshot(Base):
    __tablename__ = "daily_booking_snapshots"

    snapshot_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    room_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("room_types.room_type_id"), nullable=False, index=True)
    stay_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    rooms_booked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rooms_available: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    occupancy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    adr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pickup_1d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pickup_3d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pickup_7d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pickup_14d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pickup_30d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("idx_snapshot_lookup", "hotel_id", "room_type_id", "stay_date", "snapshot_date"),
    )
