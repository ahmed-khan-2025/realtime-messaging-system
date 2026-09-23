from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    UniqueConstraint
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow():

    return datetime.now(timezone.utc)


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )


class Room(Base):

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )


class RoomMember(Base):

    __tablename__ = "room_members"

    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "user_id",
            name="uq_room_user"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    room_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rooms.id",
            ondelete="CASCADE"
        )
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        )
    )


class Message(Base):

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    room_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rooms.id",
            ondelete="CASCADE"
        ),
        index=True
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    content: Mapped[str] = mapped_column(
        Text()
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True
    )