import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

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
        DateTime,
        default=lambda: datetime.now(UTC),
    )
