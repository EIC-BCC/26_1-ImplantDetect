from sqlalchemy import Column, Integer
from models.entities.base import Base
from datetime import datetime
from sqlalchemy import DateTime, String, Float

class ProcessResults(Base):
    __tablename__ = 'process_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    process_id = Column(Integer, nullable=False)
    class_id = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    bounding_box = Column(String, nullable=False)
    probability = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    message = Column(String, nullable=True)