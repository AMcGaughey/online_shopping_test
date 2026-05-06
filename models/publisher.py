from sqlalchemy import Column, Integer, String
from .base import Base

class Publisher(Base):
    __tablename__ = "publisher"

    publisher_id = Column(Integer, primary_key=True, autoincrement=True)
    publisher = Column(String(150))
    email = Column(String(150))
    phone = Column(String(20))
    website = Column(String(255))
