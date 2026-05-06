from flask import Flask, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models.base import Base

# Import blueprints
from routes.auth import auth_bp
from routes.shop import shop_bp
from routes.manager import manager_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ---------------------------------------
# DATABASE SETUP
# ---------------------------------------
# Create SQLAlchemy engine for MySQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(engine)

# ---------------------------------------
# DB SESSION PER REQUEST
# ---------------------------------------
@app.before_request
def create_session():
    """
    Creates a new database session before each request.
    Accessible via: app.db
    """
    app.db = SessionLocal()

@app.teardown_request
def shutdown_session(exception=None):
    """
    Closes the database session after each request.
    """
    db = getattr(app, "db", None)
    if db:
        db.close()

# ---------------------------------------
# HOME ROUTE
# ---------------------------------------
@app.route("/")
def home():
    return redirect("/login")

# ---------------------------------------
# REGISTER BLUEPRINTS
# ---------------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(manager_bp)

# ---------------------------------------
# RUN APP
# ---------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
