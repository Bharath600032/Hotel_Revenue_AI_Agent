"""
Service executing Data Import batch processing, transaction management, and snapshot recalculations.
"""
import time
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.imports.parser import DataImportParser
from app.schemas.import_schema import ImportPreview, ImportReport, RowError
from app.repositories.hotel_repository import hotel_repository
from app.repositories.reservation_repository import reservation_repository
from app.repositories.inventory_repository import inventory_repository
from app.models.inventory import Reservation, RoomInventory, DailyBookingSnapshot
from app.core.exceptions import ResourceNotFoundError, DataValidationError


class ImportService:
    def preview_import(self, db: Session, hotel_id: int, file_bytes: bytes, filename: str) -> ImportPreview:
        hotel_repository.get_by_id(db, hotel_id)  # Ensure hotel exists
        df = DataImportParser.parse_file_to_dataframe(file_bytes, filename)
        valid_rows, errors = DataImportParser.validate_and_clean(df)

        preview_slice = valid_rows[:5] if valid_rows else []
        return ImportPreview(
            total_rows=len(df),
            valid_rows_count=len(valid_rows),
            invalid_rows_count=len(errors),
            preview_data=preview_slice,
            errors=errors,
        )

    def process_import(
        self, db: Session, hotel_id: int, file_bytes: bytes, filename: str, user_id: int
    ) -> ImportReport:
        start_time = time.time()
        hotel = hotel_repository.get_by_id(db, hotel_id)
        if not hotel:
            raise ResourceNotFoundError("Hotel", hotel_id)

        df = DataImportParser.parse_file_to_dataframe(file_bytes, filename)
        valid_rows, errors = DataImportParser.validate_and_clean(df)

        if not valid_rows and errors:
            return ImportReport(
                success=False,
                filename=filename,
                imported_count=0,
                failed_count=len(errors),
                errors=errors,
                execution_time_seconds=round(time.time() - start_time, 4),
            )

        # Lookup room types & rate plans for this hotel
        room_types = {rt.room_type_code.upper(): rt for rt in hotel_repository.get_room_types_by_hotel(db, hotel_id)}
        rate_plans = hotel_repository.get_rate_plans_by_hotel(db, hotel_id)
        default_rate_plan_id = rate_plans[0].rate_plan_id if rate_plans else 1

        imported_count = 0
        db_errors: List[RowError] = []

        try:
            for idx, row in enumerate(valid_rows):
                rt_code = row["room_type_code"].upper()
                if rt_code not in room_types:
                    db_errors.append(
                        RowError(
                            row_number=idx + 2,
                            column="room_type_code",
                            invalid_value=rt_code,
                            reason=f"Room type '{rt_code}' does not exist for Hotel ID {hotel_id}.",
                            suggested_correction=f"Available room types: {list(room_types.keys())}",
                        )
                    )
                    continue

                room_type = room_types[rt_code]
                existing_res = reservation_repository.get_by_code(db, hotel_id, row["reservation_code"])

                if not existing_res:
                    res = Reservation(
                        hotel_id=hotel_id,
                        reservation_code=row["reservation_code"],
                        room_type_id=room_type.room_type_id,
                        rate_plan_id=default_rate_plan_id,
                        booking_date=row["booking_date"],
                        checkin_date=row["checkin_date"],
                        checkout_date=row["checkout_date"],
                        rooms_booked=row["rooms_booked"],
                        adults=row["adults"],
                        children=row["children"],
                        booking_channel=row["booking_channel"],
                        reservation_status=row["reservation_status"],
                        room_rate=row["room_rate"],
                        total_amount=row["total_amount"],
                    )
                    db.add(res)
                    imported_count += 1
                else:
                    existing_res.room_rate = row["room_rate"]
                    existing_res.total_amount = row["total_amount"]
                    existing_res.reservation_status = row["reservation_status"]
                    imported_count += 1

            db.commit()

        except Exception as exc:
            db.rollback()
            raise DataValidationError(f"Batch import database error: {str(exc)}")

        all_errors = errors + db_errors
        return ImportReport(
            success=len(all_errors) == 0,
            filename=filename,
            imported_count=imported_count,
            failed_count=len(all_errors),
            errors=all_errors,
            execution_time_seconds=round(time.time() - start_time, 4),
        )


import_service = ImportService()
