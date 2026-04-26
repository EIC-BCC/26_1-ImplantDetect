from datetime import datetime
from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from implantdetect_shared.entities.base import Base


class Process(Base):
    __tablename__ = 'process'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    image_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
