from sqlalchemy import create_engine, text
from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)

with engine.connect() as conn:
    print(conn.execute(text("SELECT 1")).fetchone())
