from sqlalchemy import Column, Integer
from models.entities.base import Base
from sqlalchemy import String

class Label(Base):
    __tablename__ = "label"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)