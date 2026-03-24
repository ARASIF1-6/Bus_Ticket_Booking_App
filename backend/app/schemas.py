from pydantic import BaseModel
from typing import Optional

class BookingCreate(BaseModel):
    passenger_name: str
    phone: str
    from_district: str
    to_district: str
    dropping_point: str
    fare: int
    travel_date: str

class BookingOut(BookingCreate):
    id: int
    status: str
    created_at: str

    class Config:
        orm_mode = True
