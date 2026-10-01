"""
Holidays, Events, and Weather ORM models.
"""
from __future__ import annotations

from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Holidays(Base):
    __tablename__ = "holidays"

    holiday_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    holiday_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    holiday_name: Mapped[str] = mapped_column(String(255), nullable=False)
    holiday_type: Mapped[str] = mapped_column(String(50), default="NATIONAL", nullable=False)
    importance: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    impact_factor: Mapped[float] = mapped_column(Float, default=1.2, nullable=False)

    __table_args__ = (
        Index("idx_holiday_date_country", "country", "holiday_date"),
    )


class Events(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), default="CONFERENCE", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expected_attendance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    importance: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    impact_factor: Mapped[float] = mapped_column(Float, default=1.3, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="EVENT_FEED", nullable=False)

    __table_args__ = (
        Index("idx_event_city_dates", "city", "start_date", "end_date"),
    )


class Weather(Base):
    __tablename__ = "weather"

    weather_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    forecast_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    temp_celsius: Mapped[float] = mapped_column(Float, default=28.0, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=28.0, nullable=False)
    rainfall_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rain_probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    condition: Mapped[str] = mapped_column(String(100), default="Sunny", nullable=False)
    weather_condition: Mapped[str] = mapped_column(String(100), default="Sunny", nullable=False)

    __table_args__ = (
        Index("idx_weather_city_date", "city", "date"),
    )
