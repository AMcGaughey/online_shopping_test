from flask import Flask, redirect, session, g
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
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


# ---------------------------------------
# DB SESSION PER REQUEST  (thread-safe via g)
# ---------------------------------------
@app.before_request
def open_db():
    g.db = SessionLocal()

@app.teardown_request
def close_db(exception=None):
    db = g.pop("db", None)
    if db:
        if exception:
            db.rollback()
        db.close()

# Expose g.db as app.db so existing routes don't need changing
@app.before_request
def expose_db():
    app.db = g.get("db")


# ---------------------------------------
# HOME ROUTE — send each role to their page
# ---------------------------------------
@app.route("/")
def home():
    role = session.get("role")
    if role == "manager":
        return redirect("/manager")
    if role == "customer":
        return redirect("/shop")
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
    app.run(debug=True, threaded=True)
