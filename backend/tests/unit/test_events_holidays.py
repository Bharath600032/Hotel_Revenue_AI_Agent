"""
Unit tests for Events & Holidays Engine and calendar demand impact calculations.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Hotel, Holidays, Events
from app.events.engine import event_holiday_engine


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


def test_holiday_and_event_multipliers():
    # Holiday importance 4 -> 1.15
    h = Holidays(country="India", holiday_date=date(2026, 10, 20), holiday_name="Diwali", importance=4)
    mult, exp = event_holiday_engine.calculate_holiday_multiplier([h])
    assert mult == 1.15

    # Event importance 5 + attendance 60,000 -> 1.0 + 0.25 + 0.15 = 1.40
    e = Events(
        city="Goa",
        event_name="Sunburn Festival",
        event_type="FESTIVAL",
        start_date=date(2026, 10, 20),
        end_date=date(2026, 10, 25),
        expected_attendance=60000,
        importance=5,
    )
    e_mult, e_exp = event_holiday_engine.calculate_event_multiplier([e])
    assert e_mult == 1.40


def test_evaluate_calendar_impact_db(db_session):
    hotel = Hotel(hotel_code="HTL_EVENT", hotel_name="Event Test Hotel", city="Goa", country="India")
    db_session.add(hotel)
    db_session.commit()

    stay_dt = date(2026, 10, 20)
    h = Holidays(country="India", holiday_date=stay_dt, holiday_name="National Holiday", importance=3)
    e = Events(
        city="Goa",
        event_name="Global Tech Summit",
        start_date=stay_dt,
        end_date=stay_dt,
        expected_attendance=15000,
        importance=4,
    )
    db_session.add_all([h, e])
    db_session.commit()

    impact = event_holiday_engine.evaluate_calendar_impact(
        db_session, hotel_id=hotel.hotel_id, stay_date=stay_dt
    )

    assert impact.hotel_id == hotel.hotel_id
    assert len(impact.active_holidays) == 1
    assert len(impact.active_events) == 1
    assert impact.composite_demand_multiplier >= 1.20
    assert impact.demand_classification in ["HIGH_DEMAND", "EXTREME_DEMAND"]
