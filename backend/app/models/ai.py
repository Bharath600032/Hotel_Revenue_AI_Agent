"""
AI Agent execution logs, ML forecasts, Price recommendations, Model registry, and User feedback ORM models.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, Index, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Forecasts(Base):
    __tablename__ = "forecasts"

    forecast_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    room_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("room_types.room_type_id"), nullable=False, index=True)
    stay_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    predicted_demand: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound: Mapped[float] = mapped_column(Float, nullable=False)
    upper_bound: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)

    __table_args__ = (
        Index("idx_forecast_lookup", "hotel_id", "room_type_id", "stay_date"),
    )


class PriceRecommendations(Base):
    __tablename__ = "price_recommendations"

    recommendation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=False, index=True)
    room_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("room_types.room_type_id"), nullable=False, index=True)
    stay_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    recommended_rate: Mapped[float] = mapped_column(Float, nullable=False)
    min_rate: Mapped[float] = mapped_column(Float, default=3000.0, nullable=False)
    max_rate: Mapped[float] = mapped_column(Float, default=30000.0, nullable=False)
    min_price_floor: Mapped[float] = mapped_column(Float, default=3000.0, nullable=False)
    max_price_ceiling: Mapped[float] = mapped_column(Float, default=30000.0, nullable=False)
    current_rate: Mapped[float] = mapped_column(Float, nullable=False)
    occupancy: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    forecast_demand: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    demand_score: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    competitor_median: Mapped[float] = mapped_column(Float, default=5000.0, nullable=False)
    competitor_median_rate: Mapped[float] = mapped_column(Float, default=5000.0, nullable=False)
    demand_index: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    price_change_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    price_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, default="", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_rec_lookup", "hotel_id", "room_type_id", "stay_date"),
    )


class AgentRuns(Base):
    __tablename__ = "agent_runs"

    agent_run_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    hotel_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("hotels.hotel_id"), nullable=True)
    request: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="COMPLETED", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    final_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class AgentToolCalls(Base):
    __tablename__ = "agent_tool_calls"

    tool_call_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    agent_run_id: Mapped[str] = mapped_column(String(100), ForeignKey("agent_runs.agent_run_id"), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    arguments: Mapped[dict] = mapped_column(JSON, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SUCCESS", nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    model_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    training_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)


class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(Integer, ForeignKey("price_recommendations.recommendation_id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    actual_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
