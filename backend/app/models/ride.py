from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Ride(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    driver_id: Mapped[int | None] = mapped_column(
        ForeignKey("drivers.id"),
        nullable=True,
        index=True
    )

    vehicle_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicles.id"),
        nullable=True,
        index=True
    )

    pickup_latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    pickup_longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    destination_latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    destination_longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    distance_km: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    estimated_fare: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="requested",
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    customer = relationship(
        "User",
        backref="rides"
    )

    driver = relationship(
        "Driver",
        backref="rides"
    )

    vehicle = relationship(
        "Vehicle",
        backref="rides"
    )