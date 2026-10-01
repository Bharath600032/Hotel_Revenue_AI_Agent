"""
Pydantic v2 schemas for Demand Forecasting Engine inputs and predictions.
"""
from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ModelPerformanceMetrics(BaseModel):
    model_name: str
    mae: float
    rmse: float
    mape: float
    wape: float
    sample_size: int


class ForecastPoint(BaseModel):
    stay_date: date
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    model_name: str
    model_version: str


class ForecastRequest(BaseModel):
    room_type_id: int
    start_date: date
    horizon_days: int = Field(default=30, ge=1, le=365)


class ForecastResponse(BaseModel):
    hotel_id: int
    room_type_id: int
    model_name: str
    model_version: str
    evaluation_metrics: ModelPerformanceMetrics
    predictions: List[ForecastPoint]
    created_at: datetime = Field(default_factory=datetime.utcnow)
