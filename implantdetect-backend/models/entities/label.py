from sqlalchemy import Column, Integer
from models.entities.base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class Label(Base):
    __tablename__ = "label"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)