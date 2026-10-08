"""
SQLAlchemy models for Length of Stay (LOS) Restrictions and Corporate Group Displacement Analysis.
"""
from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class LengthOfStayRules(Base):
    """
    Minimum Length of Stay (MLOS), CTA, CTD restrictions per stay date & room type.
    """
    __tablename__ = "length_of_stay_rules"

    los_rule_id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.room_type_id"), nullable=True, index=True)
    stay_date = Column(Date, nullable=False, index=True)

    min_length_of_stay = Column(Integer, default=1, nullable=False)
    max_length_of_stay = Column(Integer, nullable=True)
    closed_to_arrival = Column(Boolean, default=False, nullable=False)
    closed_to_departure = Column(Boolean, default=False, nullable=False)
    reason = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    hotel = relationship("Hotel")
    room_type = relationship("RoomType")


class GroupDisplacementLog(Base):
    """
    Audit log for Corporate Group Booking Displacement evaluation requests.
    """
    __tablename__ = "group_displacement_logs"

    displacement_id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.room_type_id"), nullable=False, index=True)

    group_name = Column(String(150), nullable=False)
    rooms_requested = Column(Integer, nullable=False)
    checkin_date = Column(Date, nullable=False)
    checkout_date = Column(Date, nullable=False)
    nights = Column(Integer, nullable=False)
    offered_rate = Column(Float, nullable=False)

    transient_revenue_displaced = Column(Float, nullable=False)
    proposed_group_revenue = Column(Float, nullable=False)
    net_displacement_impact = Column(Float, nullable=False)
    breakeven_group_rate = Column(Float, nullable=False)
    counter_offer_rate = Column(Float, nullable=False)

    decision = Column(String(30), nullable=False)  # ACCEPT, REJECT, COUNTER_OFFER
    rationale = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    hotel = relationship("Hotel")
    room_type = relationship("RoomType")
