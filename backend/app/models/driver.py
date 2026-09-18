from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    license_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    application_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    availability_status: Mapped[str] = mapped_column(
        String(20),
        default="offline",
        nullable=False
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        backref="driver"
    )