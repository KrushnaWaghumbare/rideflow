from pydantic import BaseModel, Field
from typing import Literal




class DriverApplyRequest(BaseModel):
    license_number: str = Field(
        min_length=5,
        max_length=50
    )

class DriverStatusUpdate(BaseModel):
    status: Literal["offline", "online"]

class DriverResponse(BaseModel):
    id: int
    user_id: int
    license_number: str
    application_status: str
    availability_status: str
    is_verified: bool

    class Config:
        from_attributes = True

