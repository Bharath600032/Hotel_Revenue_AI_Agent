"""
Unit tests for Dynamic Pricing Engine multipliers, price recommendations, and explanations.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Hotel, RoomType, RatePlan, PriceRecommendations
from app.pricing.engine import pricing_engine


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_pricing_multipliers():
    # Occupancy Multipliers
    mult90, _ = pricing_engine.calculate_occupancy_multiplier(92.0)
    assert mult90 == 1.30

    mult75, _ = pricing_engine.calculate_occupancy_multiplier(75.0)
    assert mult75 == 1.10

    mult20, _ = pricing_engine.calculate_occupancy_multiplier(20.0)
    assert mult20 == 0.90

    # Pickup Multipliers
    pm10, _ = pricing_engine.calculate_pickup_multiplier(12)
    assert pm10 == 1.12


def test_calculate_recommendation_and_approval(db_session):
    hotel = Hotel(hotel_code="HTL_PRICING", hotel_name="Pricing Hotel", city="Goa", total_rooms=100)
    db_session.add(hotel)
    db_session.commit()

    rt = RoomType(
        hotel_id=hotel.hotel_id,
        room_type_code="DELUXE",
        room_type_name="Deluxe Room",
        base_price=5000.0,
        total_inventory=30,
    )
    rp = RatePlan(hotel_id=hotel.hotel_id, rate_plan_code="STD", rate_plan_name="Standard")
    db_session.add_all([rt, rp])
    db_session.commit()

    stay_dt = date(2026, 10, 20)
    rec = pricing_engine.calculate_recommendation(
        db_session, hotel_id=hotel.hotel_id, room_type_id=rt.room_type_id, stay_date=stay_dt
    )

    assert rec.hotel_id == hotel.hotel_id
    assert rec.current_rate == 5000.0
    assert rec.recommended_rate >= rec.min_rate
    assert rec.recommended_rate <= rec.max_rate
    assert len(rec.price_reason) > 0
    assert rec.requires_approval is isinstance(rec.requires_approval, bool)

    # Check persistence in database
    db_rec = db_session.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == hotel.hotel_id).first()
    assert db_rec is not None
    assert db_rec.recommended_rate == rec.recommended_rate
