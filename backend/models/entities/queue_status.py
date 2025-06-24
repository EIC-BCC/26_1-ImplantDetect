from sqlalchemy import Column, Integer, String
from models.entities.base import Base

class QueueStatus(Base):
    __tablename__ = "queue_status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)