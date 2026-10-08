"""
Pydantic schemas for Option 5: Executive PDF Reporting & Automated BI Exports.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ExecutiveScheduleCreate(BaseModel):
    hotel_id: int
    schedule_name: str
    report_type: str = "DAILY_REVENUE"
    frequency: str = "DAILY"
    file_format: str = "PDF"
    recipients: str = "gm@hotel.com, revenue@hotel.com"
    is_active: bool = True


class ExecutiveScheduleResponse(BaseModel):
    schedule_id: int
    hotel_id: int
    schedule_name: str
    report_type: str
    frequency: str
    file_format: str
    recipients: str
    is_active: bool
    last_generated_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportGenerateRequest(BaseModel):
    hotel_id: int
    report_type: str = "DAILY_REVENUE"  # DAILY_REVENUE, WEEKLY_TREVPAR, MONTHLY_DISPLACEMENT_AUDIT, COMPETITOR_BENCHMARK
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    title: Optional[str] = None
    include_ai_summary: bool = True


class ReportExportLogResponse(BaseModel):
    export_id: int
    hotel_id: int
    schedule_id: Optional[int] = None
    report_title: str
    report_type: str
    file_format: str
    download_url: Optional[str] = None
    file_size_kb: float
    status: str
    metadata_json: Optional[Dict[str, Any]] = None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BIDatasetExportResponse(BaseModel):
    hotel_id: int
    hotel_name: str
    export_timestamp: datetime
    record_count: int
    currency: str = "INR"
    powerbi_endpoint_url: str
    tableau_endpoint_url: str
    columns: List[str]
    dataset_records: List[Dict[str, Any]]
