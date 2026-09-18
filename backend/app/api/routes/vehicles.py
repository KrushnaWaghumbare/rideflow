from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.driver import Driver
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse
)



router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(
        require_role("driver")
    ),
    db: Session = Depends(get_db)
):
    driver = (
        db.query(Driver)
        .filter(
            Driver.user_id == current_user.id
        )
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )

    if driver.application_status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver is not approved"
        )

    if not driver.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver is not verified"
        )

    vehicle = Vehicle(
        driver_id=driver.id,
        vehicle_number=vehicle_data.vehicle_number,
        vehicle_type=vehicle_data.vehicle_type,
        brand=vehicle_data.brand,
        model=vehicle_data.model,
        color=vehicle_data.color,
        is_active=True
    )

    db.add(vehicle)

    try:
        db.commit()
        db.refresh(vehicle)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle number already exists"
        )

    return vehicle

@router.get(
    "/me",
    response_model=VehicleResponse
)
def get_my_vehicle(
    current_user: User = Depends(
        require_role("driver")
    ),
    db: Session = Depends(get_db)
):
    driver = (
        db.query(Driver)
        .filter(
            Driver.user_id == current_user.id
        )
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    return vehicle

@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse
)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(
        require_role("driver")
    ),
    db: Session = Depends(get_db)
):
    driver = (
        db.query(Driver)
        .filter(
            Driver.user_id == current_user.id
        )
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    if vehicle.driver_id != driver.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this vehicle"
        )

    update_data = vehicle_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(vehicle, field, value)

    try:
        db.commit()
        db.refresh(vehicle)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle number already exists"
        )

    return vehicle