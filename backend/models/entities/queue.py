from sqlalchemy import Column, Integer, String
from models.entities.base import Base
from datetime import datetime
from sqlalchemy import DateTime

class Queue(Base):
    __tablename__ = "queue"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, index=True)
    id_status = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    user_id = Column(Integer, index=True)
    job_id = Column(Integer, nullable=True)  # ID do job no Beanstalkd