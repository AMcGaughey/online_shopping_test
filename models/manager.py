from sqlalchemy import Column, Integer, String
from .base import Base

class Manager(Base):
    __tablename__ = "manager"

    manager_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(150), unique=True)
    password = Column(String(255))
