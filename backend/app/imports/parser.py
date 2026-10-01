"""
Data Import Engine Parser for normalizing CSV, Excel, and JSON reservation feeds.
"""
import io
import json
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from app.schemas.import_schema import RowError, ImportPreview, ImportReport


class DataImportParser:
    """Parser & Validator for hotel reservation and inventory datasets."""

    REQUIRED_RESERVATION_COLUMNS = {
        "reservation_code",
        "room_type_code",
        "booking_date",
        "checkin_date",
        "checkout_date",
        "room_rate",
    }

    COLUMN_ALIAS_MAP = {
        "res_code": "reservation_code",
        "booking_ref": "reservation_code",
        "pnr": "reservation_code",
        "room_type": "room_type_code",
        "room_category": "room_type_code",
        "booked_on": "booking_date",
        "arrival_date": "checkin_date",
        "check_in": "checkin_date",
        "check_out": "checkout_date",
        "departure_date": "checkout_date",
        "rate": "room_rate",
        "price": "room_rate",
        "adr": "room_rate",
        "channel": "booking_channel",
        "status": "reservation_status",
    }

    @classmethod
    def clean_column_name(cls, col: str) -> str:
        cleaned = re.sub(r"[^\w\s]", "", str(col)).strip().lower().replace(" ", "_")
        return cls.COLUMN_ALIAS_MAP.get(cleaned, cleaned)

    @classmethod
    def parse_file_to_dataframe(cls, file_bytes: bytes, filename: str) -> pd.DataFrame:
        filename_lower = filename.lower()
        if filename_lower.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif filename_lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        elif filename_lower.endswith(".json"):
            data = json.loads(file_bytes.decode("utf-8"))
            if isinstance(data, dict) and "reservations" in data:
                data = data["reservations"]
            df = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported file format '{filename}'. Supported: .csv, .xlsx, .json")

        df.columns = [cls.clean_column_name(c) for c in df.columns]
        return df

    @classmethod
    def normalize_date(cls, val: Any) -> Tuple[Optional[date], Optional[str]]:
        if pd.isna(val) or val is None:
            return None, "Date value is empty or missing."

        if isinstance(val, (datetime, date)):
            return val.date() if isinstance(val, datetime) else val, None

        val_str = str(val).strip()
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
            try:
                dt = datetime.strptime(val_str, fmt).date()
                return dt, None
            except ValueError:
                continue

        return None, f"Could not parse date string '{val}'. Expected YYYY-MM-DD or DD-MM-YYYY."

    @classmethod
    def normalize_float(cls, val: Any) -> Tuple[Optional[float], Optional[str]]:
        if pd.isna(val) or val is None:
            return None, "Numeric value is missing."

        if isinstance(val, (int, float)):
            return float(val), None

        val_str = str(val).strip()
        cleaned = re.sub(r"[^\d\.]", "", val_str)
        try:
            res = float(cleaned)
            if res <= 0:
                return None, "Rate must be a positive value > 0."
            return res, None
        except ValueError:
            return None, f"Invalid numeric value '{val}'. Expected a valid currency number."

    @classmethod
    def validate_and_clean(cls, df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[RowError]]:
        valid_rows: List[Dict[str, Any]] = []
        errors: List[RowError] = []

        # Check missing required columns
        missing_cols = cls.REQUIRED_RESERVATION_COLUMNS - set(df.columns)
        if missing_cols:
            errors.append(
                RowError(
                    row_number=0,
                    column="header",
                    invalid_value=list(df.columns),
                    reason=f"Missing required columns: {sorted(list(missing_cols))}",
                    suggested_correction="Ensure CSV headers include reservation_code, room_type_code, booking_date, checkin_date, checkout_date, room_rate.",
                )
            )
            return valid_rows, errors

        seen_codes = set()

        for idx, row in df.iterrows():
            row_num = idx + 2  # 1-indexed header + row index
            row_errors: List[RowError] = []

            # 1. Reservation Code
            res_code = str(row.get("reservation_code", "")).strip()
            if not res_code or res_code.lower() == "nan":
                row_errors.append(
                    RowError(
                        row_number=row_num,
                        column="reservation_code",
                        invalid_value=row.get("reservation_code"),
                        reason="Reservation code cannot be empty.",
                        suggested_correction="Provide a unique string identifier (e.g. RES-10023).",
                    )
                )
            elif res_code in seen_codes:
                row_errors.append(
                    RowError(
                        row_number=row_num,
                        column="reservation_code",
                        invalid_value=res_code,
                        reason="Duplicate reservation code in same import dataset.",
                        suggested_correction="Ensure reservation codes are distinct.",
                    )
                )
            else:
                seen_codes.add(res_code)

            # 2. Room Type Code
            rt_code = str(row.get("room_type_code", "")).strip().upper()
            if not rt_code or rt_code.lower() == "nan":
                row_errors.append(
                    RowError(
                        row_number=row_num,
                        column="room_type_code",
                        invalid_value=row.get("room_type_code"),
                        reason="Room type code cannot be empty.",
                        suggested_correction="Provide valid room type code (e.g. DELUXE, SUITE).",
                    )
                )

            # 3. Dates
            b_date, err_b = cls.normalize_date(row.get("booking_date"))
            if err_b:
                row_errors.append(
                    RowError(
                        row_number=row_num,
                        column="booking_date",
                        invalid_value=row.get("booking_date"),
                        reason=err_b,
                        suggested_correction="Format date as YYYY-MM-DD.",
                    )
                )

            c_in, err_in = cls.normalize_date(row.get("checkin_date"))
            if err_in:
                row_errors.append(
                    RowError(
                        row_number=row_num,
                        column="checkin_date",
                        invalid_value=row.get("checkin_date"),
                        reason=err_in,
                        suggested_correction="Format date as YYYY-MM-DD.",
                    )
                )

            c_out, err_out = cls.normalize_date(row.get("checkout_date"))
            if err_out:
                row_errors.append(
                    RowError(
                        row_number=row_num,
                        column="checkout_date",
                        invalid_value=row.get("checkout_date"),
                        reason=err_out,
                        suggested_correction="Format date as YYYY-MM-DD.",
                    )
                )

            if c_in and c_out and c_out <= c_in:
                row_errors.append(
                    RowError(
                        row_number=row_num,
                        column="checkout_date",
                        invalid_value=f"Checkin: {c_in}, Checkout: {c_out}",
                        reason="Checkout date must be after checkin date.",
                        suggested_correction="Ensure checkout_date > checkin_date.",
                    )
                )

            # 4. Room Rate
            rate, err_rate = cls.normalize_float(row.get("room_rate"))
            if err_rate:
                row_errors.append(
                    RowError(
                        row_number=row_num,
                        column="room_rate",
                        invalid_value=row.get("room_rate"),
                        reason=err_rate,
                        suggested_correction="Provide a positive floating point room rate.",
                    )
                )

            if row_errors:
                errors.extend(row_errors)
            else:
                nights = (c_out - c_in).days
                total_amt = rate * nights * int(row.get("rooms_booked", 1))
                valid_rows.append(
                    {
                        "reservation_code": res_code,
                        "room_type_code": rt_code,
                        "booking_date": b_date,
                        "checkin_date": c_in,
                        "checkout_date": c_out,
                        "rooms_booked": int(row.get("rooms_booked", 1)),
                        "adults": int(row.get("adults", 2)),
                        "children": int(row.get("children", 0)),
                        "booking_channel": str(row.get("booking_channel", "Direct")).strip(),
                        "reservation_status": str(row.get("reservation_status", "CONFIRMED")).strip().upper(),
                        "room_rate": rate,
                        "total_amount": total_amt,
                    }
                )

        return valid_rows, errors
