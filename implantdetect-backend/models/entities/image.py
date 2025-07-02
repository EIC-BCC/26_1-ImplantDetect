from sqlalchemy import Column, Integer, String
from models.entities.base import Base
from datetime import datetime
from sqlalchemy import DateTime

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_hash = Column(String, unique=True, index=True)
    file_extension = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, index=True)
    active = Column(Integer, default=1)