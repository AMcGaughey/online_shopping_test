from flask import current_app as app, Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

from models.customer import Customer
from models.manager import Manager

auth_bp = Blueprint("auth", __name__)


# ----------------------
# REGISTER (CUSTOMERS ONLY)
# ----------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    db = app.db
    error = None

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        password = request.form.get("password")

        if not email or not password:
            error = "Email and password are required."
            return render_template("register.html", error=error)

        existing = db.query(Customer).filter_by(email=email).first()
        if existing:
            error = "Email already registered."
            return render_template("register.html", error=error)

        new_customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            password=generate_password_hash(password)
        )

        try:
            db.add(new_customer)
            db.commit()
            return redirect("/login")
        except Exception:
            db.rollback()
            error = "Registration failed. Try again."

    return render_template("register.html", error=error)


# ----------------------
# LOGIN (CUSTOMER + MANAGER)
# ----------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    db = app.db
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            error = "Email and password are required."
            return render_template("login.html", error=error)

        # Try customer login first
        customer = db.query(Customer).filter_by(email=email).first()
        if customer and check_password_hash(customer.password, password):
            session["user_id"] = customer.customer_id
            session["role"] = "customer"
            return redirect("/shop")

        # Try manager login
        manager = db.query(Manager).filter_by(email=email).first()
        if manager and check_password_hash(manager.password, password):
            session["user_id"] = manager.manager_id
            session["role"] = "manager"
            return redirect("/manager")

        error = "Invalid login credentials."

    return render_template("login.html", error=error)


# ----------------------
# LOGOUT
# ----------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")