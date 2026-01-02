from sqlalchemy import Column, Integer
from models.entities.base import Base
from datetime import datetime
from sqlalchemy import DateTime, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

class ProcessResults(Base):
    __tablename__ = 'process_results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    class_id: Mapped[int] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    bb_x1_center: Mapped[float] = mapped_column(Float, nullable=True)
    bb_y1_center: Mapped[float] = mapped_column(Float, nullable=True)
    bb_x2_center: Mapped[float] = mapped_column(Float, nullable=True)
    bb_y2_center: Mapped[float] = mapped_column(Float, nullable=True)
    bb_x3_center: Mapped[float] = mapped_column(Float, nullable=True)
    bb_y3_center: Mapped[float] = mapped_column(Float, nullable=True)
    bb_x4_center: Mapped[float] = mapped_column(Float, nullable=True)
    bb_y4_center: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    message: Mapped[Optional[str]] = mapped_column(String, nullable=True)