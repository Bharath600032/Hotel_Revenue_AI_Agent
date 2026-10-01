"""
Unit tests for Data Import Engine parser, date/currency normalization, and error reporting.
"""
import pytest
import pandas as pd
from app.imports.parser import DataImportParser


def test_clean_column_name():
    assert DataImportParser.clean_column_name("Check In Date") == "checkin_date"
    assert DataImportParser.clean_column_name("ADR (₹)") == "room_rate"
    assert DataImportParser.clean_column_name("PNR") == "reservation_code"


def test_normalize_date():
    dt1, err1 = DataImportParser.normalize_date("2026-10-20")
    assert err1 is None
    assert str(dt1) == "2026-10-20"

    dt2, err2 = DataImportParser.normalize_date("20/10/2026")
    assert err2 is None
    assert str(dt2) == "2026-10-20"

    dt3, err3 = DataImportParser.normalize_date("invalid-date")
    assert dt3 is None
    assert "Could not parse" in err3


def test_normalize_float_currency():
    val1, err1 = DataImportParser.normalize_float("₹5,500.00")
    assert err1 is None
    assert val1 == 5500.0

    val2, err2 = DataImportParser.normalize_float("$120.50")
    assert err2 is None
    assert val2 == 120.5

    val3, err3 = DataImportParser.normalize_float("-50.0")
    assert val3 is None
    assert "positive value" in err3


def test_validate_and_clean_dataframe_with_row_errors():
    data = [
        {
            "reservation_code": "RES-001",
            "room_type_code": "DELUXE",
            "booking_date": "2026-09-01",
            "checkin_date": "2026-10-20",
            "checkout_date": "2026-10-22",
            "room_rate": "₹6,000",
        },
        {
            "reservation_code": "RES-002",
            "room_type_code": "SUITE",
            "booking_date": "2026-09-02",
            "checkin_date": "2026-10-25",
            "checkout_date": "2026-10-24",  # Invalid: checkout before checkin
            "room_rate": "₹12,000",
        },
    ]
    df = pd.DataFrame(data)
    valid_rows, errors = DataImportParser.validate_and_clean(df)

    assert len(valid_rows) == 1
    assert valid_rows[0]["reservation_code"] == "RES-001"
    assert len(errors) == 1
    assert errors[0].column == "checkout_date"
    assert "must be after checkin" in errors[0].reason
