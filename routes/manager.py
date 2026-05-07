from flask import current_app as app, Blueprint, render_template, request, session, redirect
from werkzeug.security import generate_password_hash
from models.inventory import Inventory
from models.customer_order import CustomerOrder
from models.book import Book
from models.customer import Customer
from models.manager import Manager
from models.store import Store

manager_bp = Blueprint("manager", __name__)


def require_manager():
    """Returns a redirect if the current session is not a manager, else None."""
    if session.get("role") != "manager":
        return redirect("/login")
    return None


def get_manager_location():
    """Return the location_id this manager is assigned to, or None."""
    db = app.db
    store = db.query(Store).filter_by(manager_id=session["user_id"]).first()
    return store.location_id if store else None


# ---------------------------
# MANAGER DASHBOARD
# ---------------------------
@manager_bp.route("/manager")
def manager_dashboard():
    guard = require_manager()
    if guard:
        return guard

    db          = app.db
    location_id = get_manager_location()

    total_books     = db.query(Book).count()
    total_customers = db.query(Customer).count()

    if location_id:
        total_inventory = db.query(Inventory).filter_by(location_id=location_id).count()
        total_orders    = db.query(CustomerOrder).filter_by(location_id=location_id).count()
        recent_orders   = (
            db.query(CustomerOrder)
            .filter_by(location_id=location_id)
            .order_by(CustomerOrder.order_id.desc())
            .limit(10)
            .all()
        )
        my_store = db.query(Store).filter_by(location_id=location_id).first()
    else:
        total_inventory = db.query(Inventory).count()
        total_orders    = db.query(CustomerOrder).count()
        recent_orders   = (
            db.query(CustomerOrder)
            .order_by(CustomerOrder.order_id.desc())
            .limit(10)
            .all()
        )
        my_store = None

    return render_template(
        "manager_dashboard.html",
        total_books=total_books,
        total_inventory=total_inventory,
        total_orders=total_orders,
        total_customers=total_customers,
        recent_orders=recent_orders,
        my_store=my_store,
        location_id=location_id,
    )


# ---------------------------
# INVENTORY PAGE (scoped to manager's location)
# ---------------------------
@manager_bp.route("/inventory")
def inventory():
    guard = require_manager()
    if guard:
        return guard

    db          = app.db
    location_id = get_manager_location()

    if location_id:
        items    = db.query(Inventory).filter_by(location_id=location_id).all()
        my_store = db.query(Store).filter_by(location_id=location_id).first()
    else:
        items    = db.query(Inventory).all()
        my_store = None

    return render_template("inventory.html", inventory=items, my_store=my_store, location_id=location_id)


# ---------------------------
# UPDATE INVENTORY ITEM (price / quantity) — own store only
# ---------------------------
@manager_bp.route("/inventory/update", methods=["POST"])
def update_inventory():
    guard = require_manager()
    if guard:
        return guard

    db          = app.db
    location_id = get_manager_location()
    isbn        = request.form.get("isbn", "").strip()
    qty         = request.form.get("quantity", "").strip()
    price       = request.form.get("price", "").strip()

    if not location_id or not isbn:
        return redirect("/inventory")

    item = db.query(Inventory).filter_by(location_id=location_id, isbn=isbn).first()
    if item:
        if qty.isdigit():
            item.quantity = int(qty)
        try:
            item.price = float(price)
        except (ValueError, TypeError):
            pass
        db.commit()

    return redirect("/inventory")


# ---------------------------
# ADD BOOK TO OWN INVENTORY
# ---------------------------
@manager_bp.route("/inventory/add", methods=["POST"])
def add_inventory():
    guard = require_manager()
    if guard:
        return guard

    db          = app.db
    location_id = get_manager_location()
    isbn        = request.form.get("isbn", "").strip()
    qty         = request.form.get("quantity", "0").strip()
    price       = request.form.get("price", "0").strip()

    if not location_id or not isbn:
        return redirect("/inventory")

    book = db.query(Book).filter_by(isbn=isbn).first()
    if not book:
        return redirect("/inventory")

    existing = db.query(Inventory).filter_by(location_id=location_id, isbn=isbn).first()
    if not existing:
        new_item = Inventory(
            location_id=location_id,
            isbn=isbn,
            quantity=int(qty) if qty.isdigit() else 0,
            price=float(price) if price else 0.0,
        )
        db.add(new_item)
        db.commit()

    return redirect("/inventory")


# ---------------------------
# ORDERS PAGE (manager sees only their store's orders)
# ---------------------------
@manager_bp.route("/orders")
def orders():
    if session.get("role") not in ("manager", "customer"):
        return redirect("/login")

    db = app.db

    if session.get("role") == "manager":
        location_id = get_manager_location()
        if location_id:
            all_orders = (
                db.query(CustomerOrder)
                .filter_by(location_id=location_id)
                .order_by(CustomerOrder.order_id.desc())
                .all()
            )
        else:
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
# ADD NEW LOCATION (store)
# ---------------------------
@manager_bp.route("/location/add", methods=["GET", "POST"])
def add_location():
    guard = require_manager()
    if guard:
        return guard

    db      = app.db
    error   = None
    success = False

    # All managers for the assignment dropdown
    all_managers = db.query(Manager).all()

    if request.method == "POST":
        address    = request.form.get("address", "").strip()
        manager_id = request.form.get("manager_id", "").strip()

        if not address:
            error = "Address is required."
        else:
            new_store = Store(
                manager_id=int(manager_id) if manager_id else None,
                address=address,
            )
            db.add(new_store)
            db.commit()
            success = True

    return render_template(
        "add_location.html",
        error=error,
        success=success,
        all_managers=all_managers,
    )


# ---------------------------
# ASSIGN MANAGER TO LOCATION
# ---------------------------
@manager_bp.route("/location/assign", methods=["GET", "POST"])
def assign_manager():
    guard = require_manager()
    if guard:
        return guard

    db      = app.db
    error   = None
    success = False

    all_stores   = db.query(Store).all()
    all_managers = db.query(Manager).all()

    if request.method == "POST":
        location_id = request.form.get("location_id", "").strip()
        manager_id  = request.form.get("manager_id", "").strip()

        if not location_id or not manager_id:
            error = "Both a location and a manager must be selected."
        else:
            store = db.query(Store).filter_by(location_id=int(location_id)).first()
            if store:
                store.manager_id = int(manager_id)
                db.commit()
                success = True
            else:
                error = "Location not found."

    return render_template(
        "assign_manager.html",
        error=error,
        success=success,
        all_stores=all_stores,
        all_managers=all_managers,
    )


# ---------------------------
# CREATE MANAGER (manager-only)
# ---------------------------
@manager_bp.route("/manager/create", methods=["GET", "POST"])
def create_manager():
    guard = require_manager()
    if guard:
        return guard

    db      = app.db
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
            db.add(new_manager)
            db.commit()
            success = True

    return render_template("create_manager.html", error=error, success=success)
