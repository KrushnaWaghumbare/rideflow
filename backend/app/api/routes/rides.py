from math import radians, sin, cos, sqrt, atan2

from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.security import require_role  
from app.models.ride import Ride
from app.models.user import User
from app.schemas.ride import (
    RideRequest,
    RideResponse,
    RideStatusUpdate
)
from app.models.driver import Driver
from app.models.vehicle import Vehicle

router = APIRouter()

ALLOWED_TRANSITIONS = {
    "requested": ["searching", "cancelled"],

    "searching": ["assigned", "cancelled"],

    "assigned": [
        "driver_arriving",
        "cancelled"
    ],

    "driver_arriving": [
        "driver_reached",
        "cancelled"
    ],

    "driver_reached": [
        "started"
    ],

    "started": [
        "completed"
    ],

    "completed": [],

    "cancelled": []
}

def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:

    earth_radius = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return round(earth_radius * c, 2)


def calculate_fare(distance_km: float) -> float:

    base_fare = 50
    per_km = 15

    fare = base_fare + (distance_km * per_km)

    return round(fare, 2)


@router.post(
    "/request",
    response_model=RideResponse,
    status_code=status.HTTP_201_CREATED
)
def request_ride(
    ride_data: RideRequest,
    current_user: User = Depends(
    require_role("customer")
),
    db: Session = Depends(get_db)
):

    distance = calculate_distance(
        ride_data.pickup_latitude,
        ride_data.pickup_longitude,
        ride_data.destination_latitude,
        ride_data.destination_longitude
    )

    fare = calculate_fare(distance)

    ride = Ride(
        customer_id=current_user.id,

        pickup_latitude=ride_data.pickup_latitude,
        pickup_longitude=ride_data.pickup_longitude,

        destination_latitude=ride_data.destination_latitude,
        destination_longitude=ride_data.destination_longitude,

        distance_km=distance,
        estimated_fare=fare,

        status="requested"
    )

    db.add(ride)
    db.commit()
    db.refresh(ride)

    return ride

@router.get(
    "/my-rides",
    response_model=list[RideResponse]
)
def get_my_rides(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rides = (
        db.query(Ride)
        .filter(Ride.customer_id == current_user.id)
        .order_by(Ride.created_at.desc())
        .all()
    )

    return rides


@router.patch(
    "/{ride_id}/status",
    response_model=RideResponse
)
def update_ride_status(
    ride_id: int,
    status_data: RideStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    ride = (
        db.query(Ride)
        .filter(Ride.id == ride_id)
        .first()
    )

    if not ride:
        raise HTTPException(
            status_code=404,
            detail="Ride not found"
        )

    current_status = ride.status
    new_status = status_data.status

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        []
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Invalid ride status transition: "
                f"{current_status} -> {new_status}"
            )
        )

    ride.status = new_status

    db.commit()
    db.refresh(ride)

    return ride


@router.post(
    "/{ride_id}/assign-driver",
    response_model=RideResponse
)
def assign_driver(
    ride_id: int,
    current_user: User = Depends(require_role("customer")),
    db: Session = Depends(get_db)
):
    ride = (
        db.query(Ride)
        .filter(Ride.id == ride_id)
        .first()
    )

    if not ride:
        raise HTTPException(
            status_code=404,
            detail="Ride not found"
        )

    if ride.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only assign a driver to your own ride"
        )

    if ride.status != "searching":
        raise HTTPException(
            status_code=409,
            detail="Ride is not searching for a driver"
        )

    driver = (
        db.query(Driver)
        .filter(
            Driver.application_status == "approved",
            Driver.is_verified == True,
            Driver.availability_status == "online"
        )
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="No available driver found"
        )

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.driver_id == driver.id,
            Vehicle.is_active == True
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Driver does not have an active vehicle"
        )

    ride.driver_id = driver.id
    ride.vehicle_id = vehicle.id
    ride.status = "assigned"

    driver.availability_status = "busy"

    db.commit()
    db.refresh(ride)

    return ride