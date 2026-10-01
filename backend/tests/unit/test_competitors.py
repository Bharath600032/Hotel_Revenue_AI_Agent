"""
Unit tests for Competitor Pricing Engine statistics, price gap calculations, and anomaly detection.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Hotel, CompetitorHotels, CompetitorRates
from app.competitors.engine import competitor_engine


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


def test_price_gap_and_percentile_calculations():
    # Hotel rate = ₹5,500, Competitor median = ₹6,200 -> Price Gap = -11.29%
    gap = competitor_engine.calculate_price_gap(5500.0, 6200.0)
    assert gap == -11.29

    rank = competitor_engine.calculate_percentile_rank(5500.0, [5000.0, 6000.0, 7000.0])
    assert rank == 33.3


def test_anomaly_detection():
    # Test suspicious low rate (< ₹300)
    is_anomaly, msg = competitor_engine.detect_anomalies([100.0, 5000.0, 5500.0], 5000.0)
    assert is_anomaly is True
    assert "Suspiciously low" in msg

    # Test suspicious high spike (> 10x median)
    is_anomaly_high, msg_high = competitor_engine.detect_anomalies([5000.0, 5200.0, 60000.0], 5000.0)
    assert is_anomaly_high is True
    assert "exceeds 10x" in msg_high

    # Test normal rates
    is_anomaly_ok, _ = competitor_engine.detect_anomalies([5000.0, 5200.0, 5800.0], 5500.0)
    assert is_anomaly_ok is False


def test_analyze_market_rates_db(db_session):
    hotel = Hotel(hotel_code="HTL_COMP", hotel_name="Comp Test Hotel", city="Goa", total_rooms=100)
    db_session.add(hotel)
    db_session.commit()

    comp1 = CompetitorHotels(hotel_id=hotel.hotel_id, competitor_name="Comp 1", city="Goa")
    comp2 = CompetitorHotels(hotel_id=hotel.hotel_id, competitor_name="Comp 2", city="Goa")
    db_session.add_all([comp1, comp2])
    db_session.commit()

    stay_dt = date(2026, 10, 20)
    rate1 = CompetitorRates(competitor_id=comp1.competitor_id, stay_date=stay_dt, rate=6000.0)
    rate2 = CompetitorRates(competitor_id=comp2.competitor_id, stay_date=stay_dt, rate=7000.0)
    db_session.add_all([rate1, rate2])
    db_session.commit()

    analysis = competitor_engine.analyze_market_rates(
        db_session, hotel_id=hotel.hotel_id, stay_date=stay_dt, my_rate=5500.0
    )

    assert analysis.competitor_count == 2
    assert analysis.competitor_median == 6500.0
    assert analysis.price_gap_pct == -15.38  # (5500 - 6500) / 6500 * 100
    assert analysis.anomaly_detected is False
