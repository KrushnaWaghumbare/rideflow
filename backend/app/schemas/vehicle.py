from typing import Literal

from pydantic import BaseModel, Field


class VehicleCreate(BaseModel):
    vehicle_number: str = Field(
        min_length=5,
        max_length=20
    )

    vehicle_type: Literal[
        "mini",
        "sedan",
        "suv"
    ]

    brand: str = Field(
        min_length=2,
        max_length=50
    )

    model: str = Field(
        min_length=1,
        max_length=50
    )

    color: str = Field(
        min_length=2,
        max_length=30
    )


class VehicleResponse(BaseModel):
    id: int
    driver_id: int
    vehicle_number: str
    vehicle_type: str
    brand: str
    model: str
    color: str
    is_active: bool

    class Config:
        from_attributes = True

class VehicleUpdate(BaseModel):
    vehicle_number: str | None = Field(
        default=None,
        min_length=5,
        max_length=20
    )

    vehicle_type: Literal[
        "mini",
        "sedan",
        "suv"
    ] | None = None

    brand: str | None = Field(
        default=None,
        min_length=2,
        max_length=50
    )

    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    color: str | None = Field(
        default=None,
        min_length=2,
        max_length=30
    )

    is_active: bool | None = None