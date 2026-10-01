"""
Repository for Reservation entity operations.
"""
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.inventory import Reservation
from app.schemas.reservation import ReservationCreate, ReservationUpdate


class ReservationRepository:
    def get_by_id(self, db: Session, reservation_id: int) -> Optional[Reservation]:
        return db.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()

    def get_by_code(self, db: Session, hotel_id: int, reservation_code: str) -> Optional[Reservation]:
        return (
            db.query(Reservation)
            .filter(
                Reservation.hotel_id == hotel_id,
                Reservation.reservation_code == reservation_code,
            )
            .first()
        )

    def get_multi(
        self,
        db: Session,
        hotel_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Reservation]:
        query = db.query(Reservation).filter(Reservation.hotel_id == hotel_id)
        if status:
            query = query.filter(Reservation.reservation_status == status)
        if start_date:
            query = query.filter(Reservation.checkin_date >= start_date)
        if end_date:
            query = query.filter(Reservation.checkin_date <= end_date)
        return query.order_by(Reservation.checkin_date.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, hotel_id: int, res_in: ReservationCreate) -> Reservation:
        res_data = res_in.model_dump()
        db_res = Reservation(hotel_id=hotel_id, **res_data)
        db.add(db_res)
        db.commit()
        db.refresh(db_res)
        return db_res

    def get_stay_date_reservations(
        self, db: Session, hotel_id: int, stay_date: date, room_type_id: Optional[int] = None
    ) -> List[Reservation]:
        """Fetch all non-cancelled reservations occupying rooms on stay_date."""
        query = db.query(Reservation).filter(
            Reservation.hotel_id == hotel_id,
            Reservation.checkin_date <= stay_date,
            Reservation.checkout_date > stay_date,
            Reservation.reservation_status != "CANCELLED",
        )
        if room_type_id:
            query = query.filter(Reservation.room_type_id == room_type_id)
        return query.all()


reservation_repository = ReservationRepository()
