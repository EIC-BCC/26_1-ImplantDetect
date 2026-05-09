from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from implantdetect_shared.entities.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Image(Base):
    __tablename__ = "images"
    __table_args__ = (
        UniqueConstraint("file_hash", "user_id", name="uq_image_hash_user"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    file_hash: Mapped[str] = mapped_column(String, index=True)
    file_extension: Mapped[str] = mapped_column(String, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    active: Mapped[int] = mapped_column(Integer, default=1)
