"""
Unit tests for Hotel Revenue Calculation Engine formulas and aggregates.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.services.revenue_calculator import revenue_calculator
from app.models import Hotel, RoomType, RatePlan, Reservation, RoomInventory


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


def test_pure_formula_calculations():
    # Occupancy
    assert revenue_calculator.calculate_occupancy(80, 100) == 80.0
    assert revenue_calculator.calculate_occupancy(0, 100) == 0.0
    assert revenue_calculator.calculate_occupancy(50, 0) == 0.0  # zero division safe

    # ADR
    assert revenue_calculator.calculate_adr(50000.0, 10) == 5000.0
    assert revenue_calculator.calculate_adr(0.0, 0) == 0.0  # zero division safe

    # RevPAR
    assert revenue_calculator.calculate_revpar(50000.0, 20) == 2500.0
    assert revenue_calculator.calculate_revpar(50000.0, 0) == 0.0


def test_calculate_period_summary_db(db_session):
    # Setup Hotel & Inventory
    hotel = Hotel(hotel_code="HTL_CALC", hotel_name="Calc Hotel", city="Goa", total_rooms=10)
    db_session.add(hotel)
    db_session.commit()

    rt = RoomType(hotel_id=hotel.hotel_id, room_type_code="DELUXE", room_type_name="Deluxe", base_price=5000.0)
    rp = RatePlan(hotel_id=hotel.hotel_id, rate_plan_code="STD", rate_plan_name="Standard")
    db_session.add_all([rt, rp])
    db_session.commit()

    stay_dt = date(2026, 10, 20)
    inv = RoomInventory(
        hotel_id=hotel.hotel_id,
        room_type_id=rt.room_type_id,
        stay_date=stay_dt,
        total_rooms=10,
        available_rooms=3,
        out_of_order=0,
        sellable_rooms=10,
    )
    db_session.add(inv)

    # 7 rooms booked at ₹6,000 each = ₹42,000 revenue
    res = Reservation(
        hotel_id=hotel.hotel_id,
        reservation_code="RES-CALC-1",
        room_type_id=rt.room_type_id,
        rate_plan_id=rp.rate_plan_id,
        booking_date=date(2026, 10, 1),
        checkin_date=stay_dt,
        checkout_date=date(2026, 10, 21),
        rooms_booked=7,
        room_rate=6000.0,
        total_amount=42000.0,
        reservation_status="CONFIRMED",
    )
    db_session.add(res)
    db_session.commit()

    summary = revenue_calculator.calculate_period_summary(
        db_session, hotel_id=hotel.hotel_id, start_date=stay_dt, end_date=stay_dt
    )

    assert summary.total_sellable_rooms == 10
    assert summary.total_occupied_rooms == 7
    assert summary.total_revenue == 42000.0
    assert summary.occupancy_pct == 70.0
    assert summary.adr == 6000.0
    assert summary.revpar == 42000.0 / 10  # 4200.0
