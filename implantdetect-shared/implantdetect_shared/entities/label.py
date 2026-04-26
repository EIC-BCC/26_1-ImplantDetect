from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from implantdetect_shared.entities.base import Base


class Label(Base):
    __tablename__ = "label"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
