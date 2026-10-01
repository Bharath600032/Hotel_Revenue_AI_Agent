"""
Pydantic v2 schemas for RoomInventory entities.
"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class RoomInventoryBase(BaseModel):
    stay_date: date
    total_rooms: int = Field(..., ge=1)
    available_rooms: int = Field(..., ge=0)
    out_of_order: int = Field(default=0, ge=0)
    sellable_rooms: int = Field(..., ge=0)


class RoomInventoryCreate(RoomInventoryBase):
    room_type_id: int


class RoomInventoryUpdate(BaseModel):
    total_rooms: Optional[int] = Field(default=None, ge=1)
    available_rooms: Optional[int] = Field(default=None, ge=0)
    out_of_order: Optional[int] = Field(default=None, ge=0)
    sellable_rooms: Optional[int] = Field(default=None, ge=0)


class RoomInventoryResponse(RoomInventoryBase):
    model_config = ConfigDict(from_attributes=True)

    inventory_id: int
    hotel_id: int
    room_type_id: int
