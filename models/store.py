from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Store(Base):
    __tablename__ = "store"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    manager_id = Column(Integer, ForeignKey("manager.manager_id"))
    address = Column(String(200))

    manager = relationship("Manager")
