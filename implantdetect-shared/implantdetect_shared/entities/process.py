from datetime import datetime, timezone
from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from implantdetect_shared.entities.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Process(Base):
    __tablename__ = "process"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    image_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("images.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
