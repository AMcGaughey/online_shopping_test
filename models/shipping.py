from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Shipping(Base):
    __tablename__ = "shipping"

    shipping_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("customer_order.order_id"))
    date = Column(DateTime)
    address = Column(String(200))

    order = relationship("CustomerOrder")
