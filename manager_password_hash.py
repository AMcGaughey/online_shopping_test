from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
from config import SQLALCHEMY_DATABASE_URI
from models.manager import Manager

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
db = Session()

for manager in db.query(Manager).all():
    manager.password = generate_password_hash(manager.password)

db.commit()
print("Manager passwords hashed.")