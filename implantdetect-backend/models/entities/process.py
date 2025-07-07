from sqlalchemy import Column, Integer
from models.entities.base import Base
from datetime import datetime
from sqlalchemy import DateTime

class Process(Base):
    __tablename__ = 'process'
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Integer, nullable=False) 
    image_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)