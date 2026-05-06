from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from .base import Base

class ItemsOrdered(Base):
    __tablename__ = "items_ordered"

    order_id = Column(Integer, ForeignKey("customer_order.order_id"), primary_key=True)
    isbn = Column(String(20), ForeignKey("book.isbn"), primary_key=True)
    quantity = Column(Integer)
    price = Column(DECIMAL(10, 2))

    order = relationship("CustomerOrder", back_populates="items")
    book = relationship("Book")
