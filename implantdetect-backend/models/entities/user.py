from sqlalchemy import Column, Integer, String
from models.entities.base import Base
from datetime import datetime
from sqlalchemy import DateTime

class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    active = Column(Integer, default=1)