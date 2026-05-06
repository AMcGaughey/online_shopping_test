from flask import current_app as app, Blueprint, render_template, request, session, redirect
from werkzeug.security import generate_password_hash
from models.inventory import Inventory
from models.customer_order import CustomerOrder
from models.book import Book
from models.customer import Customer
from models.manager import Manager

manager_bp = Blueprint("manager", __name__)

def require_manager():
    """Returns a redirect if the current session is not a manager, else None."""
    if session.get("role") != "manager":
        return redirect("/login")
    return None


# ---------------------------
# MANAGER DASHBOARD
# ---------------------------
@manager_bp.route("/manager")
def manager_dashboard():
    guard = require_manager()
    if guard: return guard

    db = app.db
    total_books     = db.query(Book).count()
    total_inventory = db.query(Inventory).count()
    total_orders    = db.query(CustomerOrder).count()
    total_customers = db.query(Customer).count()
    recent_orders   = (
        db.query(CustomerOrder)
        .order_by(CustomerOrder.order_id.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "manager_dashboard.html",
        total_books=total_books,
        total_inventory=total_inventory,
        total_orders=total_orders,
        total_customers=total_customers,
        recent_orders=recent_orders,
    )


# ---------------------------
# INVENTORY PAGE
# ---------------------------
@manager_bp.route("/inventory")
def inventory():
    guard = require_manager()
    if guard: return guard

    db = app.db
    items = db.query(Inventory).all()
    return render_template("inventory.html", inventory=items)


# ---------------------------
# ORDERS PAGE (manager sees all; customer sees own)
# ---------------------------
@manager_bp.route("/orders")
def orders():
    if session.get("role") not in ("manager", "customer"):
        return redirect("/login")

    db = app.db

    if session.get("role") == "manager":
        all_orders = (
            db.query(CustomerOrder)
            .order_by(CustomerOrder.order_id.desc())
            .all()
        )
    else:
        all_orders = (
            db.query(CustomerOrder)
            .filter_by(customer_id=session["user_id"])
            .order_by(CustomerOrder.order_id.desc())
            .all()
        )

    return render_template("orders.html", orders=all_orders)


# ---------------------------
# CREATE MANAGER (manager-only)
# ---------------------------
@manager_bp.route("/manager/create", methods=["GET", "POST"])
def create_manager():
    guard = require_manager()
    if guard: return guard

    db = app.db
    error   = None
    success = False

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name  = request.form.get("last_name", "").strip()
        email      = request.form.get("email", "").strip()
        password   = request.form.get("password", "")

        if not all([first_name, last_name, email, password]):
            error = "All fields are required."
        elif db.query(Manager).filter_by(email=email).first():
            error = "A manager with that email already exists."
        else:
            new_manager = Manager(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=generate_password_hash(password),
            )
            try:
                db.add(new_manager)
                db.commit()
                success = True
            except Exception:
                db.rollback()
                error = "Could not create manager. Please try again."

    return render_template("create_manager.html", error=error, success=success)
