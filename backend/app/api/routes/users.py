from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    get_current_user,
    require_role
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate,UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        role="customer",
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    # form_data.username will contain whatever the user typed into the "username" field (pass the email here)
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(
        require_role("admin")
    )
):
    return {
        "message": "Welcome Admin",
        "user_id": current_user.id,
        "role": current_user.role
    }