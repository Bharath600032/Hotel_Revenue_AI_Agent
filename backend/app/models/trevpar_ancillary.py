"""
SQLAlchemy ORM models for Total Revenue Management (TRevPAR) & Non-Room Revenue Streams.
"""
from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class AncillaryRevenueLog(Base):
    """
    Daily Non-Room Revenue Entries by Category (F&B, Spa, Banquets, Parking, Laundry, Other).
    """
    __tablename__ = "ancillary_revenue_logs"

    ancillary_id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    entry_date = Column(Date, nullable=False, index=True)

    category = Column(String(50), nullable=False)  # FB, SPA, BANQUET, PARKING, LAUNDRY, OTHER
    sub_category = Column(String(100), nullable=True)  # Restaurant, Room Dining, Massage, Event Hall, etc.
    revenue_amount = Column(Float, nullable=False, default=0.0)  # Amount in INR (₹)
    cover_count = Column(Integer, default=0, nullable=False)  # Meals served / Spa treatments / Guests
    cost_of_sales = Column(Float, default=0.0, nullable=False)  # Direct COGS / Cost

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    hotel = relationship("Hotel")


class AncillaryPackageRecommendation(Base):
    """
    AI-generated Non-Room Revenue Upsell Packages & Dynamic Bundle Recommendations.
    """
    __tablename__ = "ancillary_package_recommendations"

    package_id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    
    package_name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # FB, SPA, WELLNESS, EVENT_RENTAL, ALL_INCLUSIVE
    description = Column(Text, nullable=False)
    
    standalone_price = Column(Float, nullable=False)  # Regular price in INR (₹)
    recommended_bundle_price = Column(Float, nullable=False)  # AI Dynamic price in INR (₹)
    projected_conversion_uplift_pct = Column(Float, nullable=False, default=15.0)
    expected_trevpar_gain_per_room = Column(Float, nullable=False, default=250.0)
    
    is_active = Column(Boolean, default=True, nullable=False)
    strategy_reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    hotel = relationship("Hotel")
