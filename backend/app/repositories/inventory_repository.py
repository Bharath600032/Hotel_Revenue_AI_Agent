"""
Repository for RoomInventory entity operations.
"""
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.inventory import RoomInventory
from app.schemas.inventory import RoomInventoryCreate, RoomInventoryUpdate


class InventoryRepository:
    def get_by_date(
        self, db: Session, hotel_id: int, room_type_id: int, stay_date: date
    ) -> Optional[RoomInventory]:
        return (
            db.query(RoomInventory)
            .filter(
                RoomInventory.hotel_id == hotel_id,
                RoomInventory.room_type_id == room_type_id,
                RoomInventory.stay_date == stay_date,
            )
            .first()
        )

    def get_range(
        self,
        db: Session,
        hotel_id: int,
        start_date: date,
        end_date: date,
        room_type_id: Optional[int] = None,
    ) -> List[RoomInventory]:
        query = db.query(RoomInventory).filter(
            RoomInventory.hotel_id == hotel_id,
            RoomInventory.stay_date >= start_date,
            RoomInventory.stay_date <= end_date,
        )
        if room_type_id:
            query = query.filter(RoomInventory.room_type_id == room_type_id)
        return query.order_by(RoomInventory.stay_date).all()

    def upsert(
        self,
        db: Session,
        hotel_id: int,
        room_type_id: int,
        stay_date: date,
        total_rooms: int,
        available_rooms: int,
        out_of_order: int = 0,
    ) -> RoomInventory:
        inv = self.get_by_date(db, hotel_id, room_type_id, stay_date)
        sellable = max(0, total_rooms - out_of_order)
        if not inv:
            inv = RoomInventory(
                hotel_id=hotel_id,
                room_type_id=room_type_id,
                stay_date=stay_date,
                total_rooms=total_rooms,
                available_rooms=available_rooms,
                out_of_order=out_of_order,
                sellable_rooms=sellable,
            )
            db.add(inv)
        else:
            inv.total_rooms = total_rooms
            inv.available_rooms = available_rooms
            inv.out_of_order = out_of_order
            inv.sellable_rooms = sellable
        db.commit()
        db.refresh(inv)
        return inv


inventory_repository = InventoryRepository()
