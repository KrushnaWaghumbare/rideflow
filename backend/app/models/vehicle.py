from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id"),
        nullable=False,
        index=True
    )

    vehicle_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    brand: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    color: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    driver = relationship(
        "Driver",
        backref="vehicles"
    )