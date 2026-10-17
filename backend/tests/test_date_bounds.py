import pytest
from datetime import date
import pandas as pd
from app.db.session import SessionLocal
from app.services.revenue_calculator import revenue_calculator
from app.pricing.engine import pricing_engine
from app.forecasting.pipeline import forecasting_pipeline
from app.forecasting.features import feature_engineer
from app.services.trevpar_service import trevpar_service


def test_revenue_calculator_out_of_bounds_date():
    """Verify that year 2 (partial year typing 2-10-16) does not raise OutOfBoundsDatetime."""
    db = SessionLocal()
    try:
        # 1. Pickup pace with partial year 0002-10-16
        bad_date = date(2, 10, 16)
        pickup = revenue_calculator.calculate_pickup_pace(db, hotel_id=4, stay_date=bad_date)
        assert pickup is not None
        assert pickup.hotel_id == 4

        # 2. Period summary with out of bounds dates
        summary = revenue_calculator.calculate_period_summary(
            db, hotel_id=4, start_date=date(2, 10, 16), end_date=date(2026, 10, 20)
        )
        assert summary is not None
        assert summary.hotel_id == 4
    finally:
        db.close()


def test_pricing_engine_out_of_bounds_date():
    """Verify pricing engine recommendation gracefully bounds year 2."""
    db = SessionLocal()
    try:
        bad_date = date(2, 10, 16)
        rec = pricing_engine.calculate_recommendation(
            db, hotel_id=4, room_type_id=1, stay_date=bad_date
        )
        assert rec is not None
        assert rec.recommended_rate > 0
    finally:
        db.close()


def test_forecasting_pipeline_out_of_bounds_date():
    """Verify forecasting pipeline runs without OutOfBoundsDatetime on partial date."""
    db = SessionLocal()
    try:
        bad_date = date(2, 10, 16)
        forecast = forecasting_pipeline.run_pipeline(
            db, hotel_id=4, room_type_id=1, start_date=bad_date, horizon_days=7
        )
        assert forecast is not None
        assert len(forecast.predictions) > 0
    finally:
        db.close()


def test_feature_engineering_out_of_bounds_date():
    """Verify feature engineer sanitizes partial year dates in history and future."""
    db = SessionLocal()
    try:
        bad_date = date(2, 10, 16)
        records = [
            {"stay_date": bad_date, "demand": 15.0},
            {"stay_date": date(2026, 10, 15), "demand": 20.0},
        ]
        df_train, df_future = feature_engineer.build_feature_dataframe(
            historical_records=records,
            future_dates=[bad_date, date(2026, 10, 17)],
            hotel_id=4,
            db=db,
        )
        assert df_train is not None
        assert not df_train.empty
        assert df_future is not None
        assert not df_future.empty
    finally:
        db.close()


def test_trevpar_service_out_of_bounds_date():
    """Verify TRevPAR summary handles partial out of bounds dates."""
    db = SessionLocal()
    try:
        bad_date = date(2, 10, 16)
        res = trevpar_service.calculate_trevpar_summary(
            db, hotel_id=4, start_date=bad_date, end_date=date(2026, 10, 20)
        )
        assert res is not None
        assert res.hotel_id == 4
    finally:
        db.close()
