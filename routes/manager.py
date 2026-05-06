from flask import current_app as app, Blueprint, render_template, session, redirect
from models.inventory import Inventory
from models.customer_order import CustomerOrder

manager_bp = Blueprint("manager", __name__)

# ---------------------------
# MANAGER DASHBOARD
# ---------------------------
@manager_bp.route("/manager")
def manager_dashboard():
    if session.get("role") != "manager":
        return redirect("/login")

    return render_template("manager_dashboard.html")


# ---------------------------
# INVENTORY PAGE
# ---------------------------
@manager_bp.route("/inventory")
def inventory():
    db = app.db
    items = db.query(Inventory).all()
    return render_template("inventory.html", inventory=items)


# ---------------------------
# ORDERS PAGE
# ---------------------------
@manager_bp.route("/orders")
def orders():
    db = app.db
    orders = db.query(CustomerOrder).all()
    return render_template("orders.html", orders=orders)
