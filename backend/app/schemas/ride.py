from pydantic import BaseModel, Field
from typing import Literal

class RideRequest(BaseModel):
    pickup_latitude: float = Field(ge=-90, le=90)
    pickup_longitude: float = Field(ge=-180, le=180)

    destination_latitude: float = Field(ge=-90, le=90)
    destination_longitude: float = Field(ge=-180, le=180)


class RideResponse(BaseModel):
    id: int
    customer_id: int
    driver_id: int | None
    vehicle_id: int | None

    pickup_latitude: float
    pickup_longitude: float

    destination_latitude: float
    destination_longitude: float

    distance_km: float | None
    estimated_fare: float | None
    status: str

    class Config:
        from_attributes = True

class RideStatusUpdate(BaseModel):
    status: Literal[
        "searching",
        "assigned",
        "driver_arriving",
        "driver_reached",
        "started",
        "completed",
        "cancelled"
    ]