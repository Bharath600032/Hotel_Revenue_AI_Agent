"""
SQLAlchemy ORM models for Option 5: Executive PDF Reporting & Automated BI Exports.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class ExecutiveReportSchedule(Base):
    """Configuration for recurring automated PDF reports & email dispatch."""
    __tablename__ = "executive_report_schedules"

    schedule_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id", ondelete="CASCADE"), nullable=False, index=True)

    report_type = Column(String(50), nullable=False, default="DAILY_REVENUE")  # DAILY_REVENUE, WEEKLY_TREVPAR, MONTHLY_DISPLACEMENT_AUDIT, COMPETITOR_BENCHMARK
    schedule_name = Column(String(100), nullable=False)
    frequency = Column(String(20), nullable=False, default="DAILY")  # DAILY, WEEKLY, MONTHLY
    file_format = Column(String(20), nullable=False, default="PDF")  # PDF, CSV, EXCEL_BI
    recipients = Column(String(255), nullable=False, default="gm@hotel.com, revenue@hotel.com")
    is_active = Column(Boolean, nullable=False, default=True)

    last_generated_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    hotel = relationship("Hotel", backref="executive_schedules")


class ReportExportLog(Base):
    """Log history of generated executive PDF reports and BI dataset exports."""
    __tablename__ = "report_export_logs"

    export_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey("executive_report_schedules.schedule_id", ondelete="SET NULL"), nullable=True)

    report_title = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False, default="DAILY_REVENUE")
    file_format = Column(String(20), nullable=False, default="PDF")  # PDF, CSV, JSON_BI
    download_url = Column(String(500), nullable=True)
    file_size_kb = Column(Float, nullable=False, default=150.0)
    status = Column(String(20), nullable=False, default="COMPLETED")  # COMPLETED, FAILED, PROCESSING
    metadata_json = Column(JSON, nullable=True)

    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    hotel = relationship("Hotel", backref="report_export_logs")
