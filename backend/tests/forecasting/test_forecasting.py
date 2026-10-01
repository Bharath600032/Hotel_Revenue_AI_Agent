"""
Unit and Integration tests for Demand Forecasting pipeline, models, and evaluation metrics.
"""
import pytest
from datetime import date
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Hotel, RoomType, RatePlan, Reservation, Forecasts, ModelRegistry
from app.forecasting.evaluation import model_evaluator
from app.forecasting.pipeline import forecasting_pipeline


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


def test_model_evaluator_metrics():
    y_true = np.array([10.0, 20.0, 30.0, 40.0])
    y_pred = np.array([12.0, 18.0, 33.0, 38.0])

    mae = model_evaluator.calculate_mae(y_true, y_pred)
    assert mae == 2.25

    wape = model_evaluator.calculate_wape(y_true, y_pred)
    assert round(wape, 2) == 9.0

    best = model_evaluator.select_best_model({
        "ModelA": {"wape": 15.0},
        "ModelB": {"wape": 8.5},
    })
    assert best == "ModelB"


def test_forecasting_pipeline_execution(db_session):
    # Setup Hotel & RoomType
    hotel = Hotel(hotel_code="HTL_FC", hotel_name="Forecast Test Hotel", city="Mumbai", total_rooms=50)
    db_session.add(hotel)
    db_session.commit()

    rt = RoomType(hotel_id=hotel.hotel_id, room_type_code="DELUXE", room_type_name="Deluxe Room", base_price=5000.0, total_inventory=30)
    rp = RatePlan(hotel_id=hotel.hotel_id, rate_plan_code="STD", rate_plan_name="Standard")
    db_session.add_all([rt, rp])
    db_session.commit()

    # Execute Forecast Pipeline for 7 days horizon
    start_dt = date(2026, 10, 1)
    res = forecasting_pipeline.run_pipeline(
        db_session,
        hotel_id=hotel.hotel_id,
        room_type_id=rt.room_type_id,
        start_date=start_dt,
        horizon_days=7,
    )

    assert res.hotel_id == hotel.hotel_id
    assert res.room_type_id == rt.room_type_id
    assert len(res.predictions) == 7
    assert res.predictions[0].confidence_score > 0.0

    # Verify persisted in database
    db_fcs = db_session.query(Forecasts).filter(Forecasts.hotel_id == hotel.hotel_id).all()
    assert len(db_fcs) == 7
