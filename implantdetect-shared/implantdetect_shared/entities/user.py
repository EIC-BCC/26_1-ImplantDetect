from sqlalchemy import Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from implantdetect_shared.entities.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    active: Mapped[int] = mapped_column(Integer, default=1)
