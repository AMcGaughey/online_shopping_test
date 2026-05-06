from sqlalchemy import Column, Integer, ForeignKey, DateTime, DECIMAL, String
from sqlalchemy.orm import relationship
from .base import Base

class CustomerOrder(Base):
    __tablename__ = "customer_order"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("store.location_id"))
    customer_id = Column(Integer, ForeignKey("customer.customer_id"))
    date = Column(DateTime)
    total = Column(DECIMAL(10, 2))
    status = Column(String(50))

    customer = relationship("Customer")
    store = relationship("Store")
    items = relationship("ItemsOrdered", back_populates="order")
    shipping = relationship("Shipping", uselist=False)
