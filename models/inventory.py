from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from .base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    location_id = Column(Integer, ForeignKey("store.location_id"), primary_key=True)
    isbn = Column(String(20), ForeignKey("book.isbn"), primary_key=True)
    quantity = Column(Integer)
    price = Column(DECIMAL(10, 2))

    store = relationship("Store")
    book = relationship("Book")
