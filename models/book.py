from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Book(Base):
    __tablename__ = "book"

    isbn = Column(String(20), primary_key=True)
    publisher_id = Column(Integer, ForeignKey("publisher.publisher_id"))
    upc = Column(String(20))
    title = Column(String(255))
    genre = Column(String(100))
    cover_type = Column(String(50))
    release_year = Column(Integer)

    publisher = relationship("Publisher")
    authors = relationship("Author", secondary="writes")
