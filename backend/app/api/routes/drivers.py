from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.driver import Driver
from app.models.user import User
from app.schemas.driver import (
    DriverApplyRequest,
    DriverResponse,
    DriverStatusUpdate
)


router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"]
)


@router.post(
    "/apply",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED
)
def apply_as_driver(
    driver_data: DriverApplyRequest,
    current_user: User = Depends(
        require_role("customer")
    ),
    db: Session = Depends(get_db)
):
    existing_driver = (
        db.query(Driver)
        .filter(Driver.user_id == current_user.id)
        .first()
    )

    if existing_driver:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Driver application already exists"
        )

    existing_license = (
        db.query(Driver)
        .filter(
            Driver.license_number
            == driver_data.license_number
        )
        .first()
    )

    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="License number already exists"
        )

    driver = Driver(
        user_id=current_user.id,
        license_number=driver_data.license_number,
        status="pending",
        is_verified=False
    )

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return driver


@router.patch(
    "/{driver_id}/approve",
    response_model=DriverResponse
)
def approve_driver(
    driver_id: int,
    current_user: User = Depends(
        require_role("admin")
    ),
    db: Session = Depends(get_db)
):
    driver = (
        db.query(Driver)
        .filter(Driver.id == driver_id)
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver application not found"
        )

    if driver.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Driver is already approved"
        )

    driver.application_status = "approved"
    driver.is_verified = True

    driver_user = (
        db.query(User)
        .filter(User.id == driver.user_id)
        .first()
    )

    if not driver_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user not found"
        )

    driver_user.role = "driver"

    db.commit()
    db.refresh(driver)

    return driver


@router.get(
    "/me",
    response_model=DriverResponse
)
def get_my_driver_profile(
    current_user: User = Depends(
        require_role("driver")
    ),
    db: Session = Depends(get_db)
):
    driver = (
        db.query(Driver)
        .filter(Driver.user_id == current_user.id)
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )

    return driver


@router.patch(
    "/status",
    response_model=DriverResponse
)
def update_driver_status(
    status_data: DriverStatusUpdate,
    current_user: User = Depends(
        require_role("driver")
    ),
    db: Session = Depends(get_db)
):
    driver = (
        db.query(Driver)
        .filter(Driver.user_id == current_user.id)
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

    if driver.availability_status == "busy":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Busy driver cannot manually change status"
        )

    driver.availability_status = status_data.status

    db.commit()
    db.refresh(driver)

    return driver