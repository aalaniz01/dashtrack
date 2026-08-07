import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # unique ID for user
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # email for user
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    # hashed_password for user
    hashed_password: Mapped[str] = mapped_column()

    # timestamp of creation of the user
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    # relationship one-to-many
    shifts: Mapped[list["Shift"]] = relationship(
        back_populates="user",
    )


class Shift(Base):
    __tablename__ = "shifts"

    __table_args__ = (
        CheckConstraint(
            "starting_odometer_miles >= 0",
            name="ck_shifts_starting_odometer_nonnegative",
        ),
        CheckConstraint(
            "(ended_at IS NULL AND ending_odometer_miles IS NULL) "
            "OR (ended_at IS NOT NULL AND ending_odometer_miles IS NOT NULL)",
            name="ck_shifts_end_fields_together",
        ),
        CheckConstraint(
            "ended_at IS NULL OR ended_at > started_at",
            name="ck_shifts_ended_after_started",
        ),
        CheckConstraint(
            "ending_odometer_miles IS NULL "
            "OR ending_odometer_miles >= starting_odometer_miles",
            name="ck_shifts_ending_odometer_not_before_start",
        ),
        Index(
            "ux_shifts_one_active_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("ended_at IS NULL"),
        ),
    )
    # unique id for the shift
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # foreign key mapped to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
    )

    # time start the shift
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # time end the shift
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    # starting  miles
    starting_odometer_miles: Mapped[Decimal] = mapped_column(
        Numeric(7, 1),
    )

    # ending miles
    ending_odometer_miles: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 1),
    )

    # time it was created
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    # relationship
    user: Mapped["User"] = relationship(
        back_populates="shifts",
    )
