from sqlalchemy import Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from implantdetect_shared.entities.base import Base


class Image(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    file_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    file_extension: Mapped[str] = mapped_column(String, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    active: Mapped[int] = mapped_column(Integer, default=1)
