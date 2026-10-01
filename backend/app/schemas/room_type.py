"""
Pydantic v2 schemas for RoomType master data.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RoomTypeBase(BaseModel):
    room_type_code: str = Field(..., min_length=2, max_length=50)
    room_type_name: str = Field(..., min_length=2, max_length=100)
    max_occupancy: int = Field(default=2, ge=1, le=10)
    base_price: float = Field(..., gt=0.0)
    total_inventory: int = Field(default=25, ge=1)
    status: str = Field(default="ACTIVE", max_length=20)


class RoomTypeCreate(RoomTypeBase):
    pass


class RoomTypeUpdate(BaseModel):
    room_type_name: Optional[str] = None
    max_occupancy: Optional[int] = Field(default=None, ge=1, le=10)
    base_price: Optional[float] = Field(default=None, gt=0.0)
    total_inventory: Optional[int] = Field(default=None, ge=1)
    status: Optional[str] = None


class RoomTypeResponse(RoomTypeBase):
    model_config = ConfigDict(from_attributes=True)

    room_type_id: int
    hotel_id: int
