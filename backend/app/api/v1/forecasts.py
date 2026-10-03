"""
Demand Forecasting REST API endpoints.
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.forecast import ForecastResponse, ForecastRequest
from app.forecasting.pipeline import forecasting_pipeline
from app.models.ai import Forecasts
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}/forecasts", tags=["Demand Forecasting"])


@router.post("/run", response_model=ForecastResponse, status_code=status.HTTP_201_CREATED)
async def run_forecast(
    hotel_id: int,
    payload: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Analyst"])),
):
    """Execute multi-model demand forecasting pipeline for room type and stay horizon."""
    verify_hotel_access(hotel_id, current_user, db)
    return forecasting_pipeline.run_pipeline(
        db,
        hotel_id=hotel_id,
        room_type_id=payload.room_type_id,
        start_date=payload.start_date,
        horizon_days=payload.horizon_days,
    )


@router.get("", response_model=List[dict])
async def get_forecasts(
    hotel_id: int,
    room_type_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve persisted demand forecasts for stay date range (auto-runs pipeline if empty or flat)."""
    verify_hotel_access(hotel_id, current_user, db)
    fcs = (
        db.query(Forecasts)
        .filter(
            Forecasts.hotel_id == hotel_id,
            Forecasts.room_type_id == room_type_id,
            Forecasts.stay_date >= start_date,
            Forecasts.stay_date <= end_date,
        )
        .order_by(Forecasts.stay_date)
        .all()
    )

    # Check if forecasts are empty or flat (all values identical)
    is_flat = False
    if fcs and len(fcs) > 1:
        vals = [f.predicted_demand for f in fcs]
        if len(set(vals)) <= 1:
            is_flat = True

    if not fcs or is_flat:
        forecasting_pipeline.run_pipeline(
            db,
            hotel_id=hotel_id,
            room_type_id=room_type_id,
            start_date=start_date,
            horizon_days=30,
        )
        fcs = (
            db.query(Forecasts)
            .filter(
                Forecasts.hotel_id == hotel_id,
                Forecasts.room_type_id == room_type_id,
                Forecasts.stay_date >= start_date,
                Forecasts.stay_date <= end_date,
            )
            .order_by(Forecasts.stay_date)
            .all()
        )

    return [
        {
            "stay_date": f.stay_date,
            "predicted_demand": f.predicted_demand,
            "lower_bound": f.lower_bound,
            "upper_bound": f.upper_bound,
            "confidence_score": f.confidence_score,
            "model_name": f.model_name,
        }
        for f in fcs
    ]
