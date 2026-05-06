from flask import current_app as app, Blueprint, render_template, request, redirect, session

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
        last_name  = request.form.get("last_name")
        email      = request.form.get("email")
        phone      = request.form.get("phone")
        address    = request.form.get("address")
        password   = request.form.get("password")   # now plain text

        if not email or not password:
            error = "Email and password are required."
            return render_template("register.html", error=error)

        # Check if email already exists
        existing = db.query(Customer).filter_by(email=email).first()
        if existing:
            error = "Email already registered."
            return render_template("register.html", error=error)

        # Store password AS-IS (plain 8-digit numeric)
        new_customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            password=password
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
# LOGIN (NO HASHING)
# ----------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    db = app.db
    error = None

    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()   # plain text

        if not email or not password:
            error = "Email and password are required."
            return render_template("login.html", error=error)

        # ----------------------
        # Try MANAGER login
        # ----------------------
        manager = db.query(Manager).filter_by(email=email).first()
        if manager and manager.password == password:   # plain comparison
            session["user_id"] = manager.manager_id
            session["role"]    = "manager"
            session["name"]    = f"{manager.first_name} {manager.last_name}"
            return redirect("/manager")

        # ----------------------
        # Try CUSTOMER login
        # ----------------------
        customer = db.query(Customer).filter_by(email=email).first()
        if customer and customer.password == password:  # plain comparison
            session["user_id"] = customer.customer_id
            session["role"]    = "customer"
            session["name"]    = f"{customer.first_name} {customer.last_name}"
            session["address"] = customer.address or ""
            return redirect("/shop")

        # If neither matched
        error = "Invalid email or password."

    return render_template("login.html", error=error)


# ----------------------
# LOGOUT
# ----------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
