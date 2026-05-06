from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class Writes(Base):
    __tablename__ = "writes"

    isbn = Column(String(20), ForeignKey("book.isbn"), primary_key=True)
    author_id = Column(Integer, ForeignKey("author.author_id"), primary_key=True)
