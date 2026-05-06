from flask import current_app as app, Blueprint, render_template, session, redirect
from models.inventory import Inventory
from models.customer_order import CustomerOrder
from models.book import Book
from models.customer import Customer

manager_bp = Blueprint("manager", __name__)


# ---------------------------
# MANAGER DASHBOARD
# ---------------------------
@manager_bp.route("/manager")
def manager_dashboard():
    if session.get("role") != "manager":
        return redirect("/login")

    db = app.db
    total_books     = db.query(Book).count()
    total_inventory = db.query(Inventory).count()
    total_orders    = db.query(CustomerOrder).count()
    total_customers = db.query(Customer).count()
    recent_orders   = db.query(CustomerOrder).order_by(CustomerOrder.order_id.desc()).limit(10).all()

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
    if session.get("role") != "manager":
        return redirect("/login")

    db = app.db
    items = db.query(Inventory).all()
    return render_template("inventory.html", inventory=items)


# ---------------------------
# ORDERS PAGE
# ---------------------------
@manager_bp.route("/orders")
def orders():
    if session.get("role") not in ("manager", "customer"):
        return redirect("/login")

    db = app.db

    if session.get("role") == "manager":
        all_orders = db.query(CustomerOrder).order_by(CustomerOrder.order_id.desc()).all()
    else:
        all_orders = (
            db.query(CustomerOrder)
            .filter_by(customer_id=session["user_id"])
            .order_by(CustomerOrder.order_id.desc())
            .all()
        )

    return render_template("orders.html", orders=all_orders)
