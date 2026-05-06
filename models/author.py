from sqlalchemy import Column, Integer, String
from .base import Base

class Author(Base):
    __tablename__ = "author"

    author_id = Column(Integer, primary_key=True, autoincrement=True)
    author_first_name = Column(String(100))
    author_last_name = Column(String(100))
