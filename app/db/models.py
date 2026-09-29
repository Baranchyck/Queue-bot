from datetime import datetime

from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Index, String,
    UniqueConstraint, func, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Queue(Base):
    __tablename__ = "queues"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    owner_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index(
            "uq_queue_active_chat",
            "chat_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )


class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    queue_id: Mapped[int] = mapped_column(ForeignKey("queues.id", ondelete="CASCADE"))
    position: Mapped[int]
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    user_name: Mapped[str | None] = mapped_column(String(100))

    __table_args__ = (
        UniqueConstraint("queue_id", "position", name="uq_slot_position"),
        Index(
            "uq_slot_user",
            "queue_id", "user_id",
            unique=True,
            postgresql_where=text("user_id IS NOT NULL"),
        ),
    )