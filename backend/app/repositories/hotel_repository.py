"""
Repository for Hotel, RoomType, and RatePlan database operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.hotel import Hotel, RoomType, RatePlan
from app.schemas.hotel import HotelCreate, HotelUpdate
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate
from app.schemas.rate_plan import RatePlanCreate, RatePlanUpdate


class HotelRepository:
    # --- Hotel Operations ---
    def get_by_id(self, db: Session, hotel_id: int) -> Optional[Hotel]:
        return db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()

    def get_by_code(self, db: Session, hotel_code: str) -> Optional[Hotel]:
        return db.query(Hotel).filter(Hotel.hotel_code == hotel_code.upper()).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        city: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Hotel]:
        query = db.query(Hotel)
        if city:
            query = query.filter(Hotel.city.ilike(f"%{city}%"))
        if status:
            query = query.filter(Hotel.status == status)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, hotel_in: HotelCreate) -> Hotel:
        hotel_data = hotel_in.model_dump()
        hotel_data["hotel_code"] = hotel_data["hotel_code"].upper()
        db_hotel = Hotel(**hotel_data)
        db.add(db_hotel)
        db.commit()
        db.refresh(db_hotel)
        return db_hotel

    def update(self, db: Session, db_hotel: Hotel, hotel_in: HotelUpdate) -> Hotel:
        update_data = hotel_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_hotel, field, value)
        db.commit()
        db.refresh(db_hotel)
        return db_hotel

    # --- RoomType Operations ---
    def get_room_type(self, db: Session, room_type_id: int) -> Optional[RoomType]:
        return db.query(RoomType).filter(RoomType.room_type_id == room_type_id).first()

    def get_room_types_by_hotel(self, db: Session, hotel_id: int) -> List[RoomType]:
        return db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()

    def create_room_type(self, db: Session, hotel_id: int, rt_in: RoomTypeCreate) -> RoomType:
        rt_data = rt_in.model_dump()
        db_rt = RoomType(hotel_id=hotel_id, **rt_data)
        db.add(db_rt)
        db.commit()
        db.refresh(db_rt)
        return db_rt

    def update_room_type(self, db: Session, db_rt: RoomType, rt_in: RoomTypeUpdate) -> RoomType:
        update_data = rt_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rt, field, value)
        db.commit()
        db.refresh(db_rt)
        return db_rt

    # --- RatePlan Operations ---
    def get_rate_plan(self, db: Session, rate_plan_id: int) -> Optional[RatePlan]:
        return db.query(RatePlan).filter(RatePlan.rate_plan_id == rate_plan_id).first()

    def get_rate_plans_by_hotel(self, db: Session, hotel_id: int) -> List[RatePlan]:
        return db.query(RatePlan).filter(RatePlan.hotel_id == hotel_id).all()

    def create_rate_plan(self, db: Session, hotel_id: int, rp_in: RatePlanCreate) -> RatePlan:
        rp_data = rp_in.model_dump()
        db_rp = RatePlan(hotel_id=hotel_id, **rp_data)
        db.add(db_rp)
        db.commit()
        db.refresh(db_rp)
        return db_rp

    def update_rate_plan(self, db: Session, db_rp: RatePlan, rp_in: RatePlanUpdate) -> RatePlan:
        update_data = rp_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rp, field, value)
        db.commit()
        db.refresh(db_rp)
        return db_rp


hotel_repository = HotelRepository()
