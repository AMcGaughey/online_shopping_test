from sqlalchemy import Column, Integer, String
from .base import Base

class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(150), unique=True)
    phone = Column(String(20))
    address = Column(String(200))
    password = Column(String(255))
