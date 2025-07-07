from sqlalchemy import Column, Integer, String
from models.entities.base import Base
from datetime import datetime
from sqlalchemy import DateTime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column

class Image(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    file_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    file_extension: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    active: Mapped[int] = mapped_column(Integer, default=1)