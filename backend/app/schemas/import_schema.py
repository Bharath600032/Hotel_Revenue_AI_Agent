"""
Pydantic v2 schemas for Data Import Engine validation, error reporting, and previews.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RowError(BaseModel):
    row_number: int
    column: str
    invalid_value: Any
    reason: str
    suggested_correction: str


class ImportPreview(BaseModel):
    total_rows: int
    valid_rows_count: int
    invalid_rows_count: int
    preview_data: List[Dict[str, Any]]
    errors: List[RowError]


class ImportReport(BaseModel):
    success: bool
    filename: str
    imported_count: int
    failed_count: int
    errors: List[RowError]
    execution_time_seconds: float
