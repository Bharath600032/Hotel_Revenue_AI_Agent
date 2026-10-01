"""
Unit tests for Pricing Guardrails & Safety Controls Engine.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Hotel, RoomType
from app.services.pricing_guardrails import pricing_guardrails_engine


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


def test_guardrail_clamping_max_daily_increase(db_session):
    hotel = Hotel(hotel_code="HTL_GUARD", hotel_name="Guardrail Hotel", city="Goa", total_rooms=50)
    db_session.add(hotel)
    db_session.commit()

    rt = RoomType(
        hotel_id=hotel.hotel_id,
        room_type_code="DELUXE",
        room_type_name="Deluxe Room",
        base_price=5000.0,
    )
    db_session.add(rt)
    db_session.commit()

    # Current rate = ₹5,000. Proposed rate = ₹7,000 (+40% increase)
    # Max daily increase limit = 20% (max ₹6,000)
    res = pricing_guardrails_engine.validate_and_clamp_rate(
        db_session,
        hotel_id=hotel.hotel_id,
        room_type_id=rt.room_type_id,
        stay_date=date(2026, 10, 20),
        proposed_rate=7000.0,
        current_rate=5000.0,
    )

    assert res.was_clamped is True
    assert res.clamped_safe_rate == 6000.0
    assert res.requires_approval is True
    assert len(res.violations) >= 1
    assert res.violations[0].rule_name == "MAX_DAILY_INCREASE_LIMIT"


def test_guardrail_safe_price_variation(db_session):
    hotel = Hotel(hotel_code="HTL_SAFE", hotel_name="Safe Hotel", city="Goa", total_rooms=50)
    db_session.add(hotel)
    db_session.commit()

    rt = RoomType(
        hotel_id=hotel.hotel_id,
        room_type_code="DELUXE",
        room_type_name="Deluxe Room",
        base_price=5000.0,
    )
    db_session.add(rt)
    db_session.commit()

    # Current rate = ₹5,000. Proposed rate = ₹5,300 (+6% increase < 10% threshold)
    res = pricing_guardrails_engine.validate_and_clamp_rate(
        db_session,
        hotel_id=hotel.hotel_id,
        room_type_id=rt.room_type_id,
        stay_date=date(2026, 10, 20),
        proposed_rate=5300.0,
        current_rate=5000.0,
    )

    assert res.was_clamped is False
    assert res.clamped_safe_rate == 5300.0
    assert res.requires_approval is False
    assert res.status == "SAFE"
