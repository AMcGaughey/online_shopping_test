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
    if session.get("role") != "manager":
        return redirect("/login")
    return None


def get_manager_store():
    """Return the Store row this manager is assigned to, or None."""
    db = app.db
    return db.query(Store).filter_by(manager_id=session.get("user_id")).first()


# ---------------------------
# MANAGER DASHBOARD
# ---------------------------
@manager_bp.route("/manager")
def manager_dashboard():
    guard = require_manager()
    if guard:
        return guard

    db       = app.db
    my_store = get_manager_store()
    loc_id   = my_store.location_id if my_store else None

    total_books     = db.query(Book).count()
    total_customers = db.query(Customer).count()

    if loc_id:
        total_inventory = db.query(Inventory).filter_by(location_id=loc_id).count()
        total_orders    = db.query(CustomerOrder).filter_by(location_id=loc_id).count()
        recent_orders   = (
            db.query(CustomerOrder)
            .filter_by(location_id=loc_id)
            .order_by(CustomerOrder.order_id.desc())
            .limit(10)
            .all()
        )
    else:
        total_inventory = db.query(Inventory).count()
        total_orders    = db.query(CustomerOrder).count()
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
        my_store=my_store,
        location_id=loc_id,
    )


# ---------------------------
# INVENTORY PAGE (scoped to manager's store)
# ---------------------------
@manager_bp.route("/inventory")
def inventory():
    guard = require_manager()
    if guard:
        return guard

    db       = app.db
    my_store = get_manager_store()
    loc_id   = my_store.location_id if my_store else None

    if loc_id:
        items = db.query(Inventory).filter_by(location_id=loc_id).all()
    else:
        items = db.query(Inventory).all()

    # All books (for the "add item" dropdown)
    all_books = db.query(Book).order_by(Book.title).all()

    return render_template(
        "inventory.html",
        inventory=items,
        my_store=my_store,
        location_id=loc_id,
        all_books=all_books,
    )


# ---------------------------
# UPDATE INVENTORY (qty + price) — own store only
# ---------------------------
@manager_bp.route("/inventory/update", methods=["POST"])
def update_inventory():
    guard = require_manager()
    if guard:
        return guard

    db     = app.db
    store  = get_manager_store()
    loc_id = store.location_id if store else None
    isbn   = request.form.get("isbn", "").strip()

    if not loc_id or not isbn:
        return redirect("/inventory")

    item = db.query(Inventory).filter_by(location_id=loc_id, isbn=isbn).first()
    if item:
        try:
            item.quantity = int(request.form.get("quantity", item.quantity))
        except ValueError:
            pass
        try:
            item.price = float(request.form.get("price", item.price))
        except ValueError:
            pass
        db.commit()

    return redirect("/inventory")


# ---------------------------
# MANUALLY ADD INVENTORY ITEM — own store only
# ---------------------------
@manager_bp.route("/inventory/add", methods=["POST"])
def add_inventory():
    guard = require_manager()
    if guard:
        return guard

    db     = app.db
    store  = get_manager_store()
    loc_id = store.location_id if store else None
    isbn   = request.form.get("isbn", "").strip()

    if not loc_id or not isbn:
        return redirect("/inventory")

    # Confirm the book exists
    book = db.query(Book).filter_by(isbn=isbn).first()
    if not book:
        return redirect("/inventory")

    # If already in inventory, just update; otherwise insert
    existing = db.query(Inventory).filter_by(location_id=loc_id, isbn=isbn).first()
    try:
        qty   = int(request.form.get("quantity", 0))
        price = float(request.form.get("price", 0.00))
    except ValueError:
        return redirect("/inventory")

    if existing:
        existing.quantity = qty
        existing.price    = price
    else:
        db.add(Inventory(location_id=loc_id, isbn=isbn, quantity=qty, price=price))

    db.commit()
    return redirect("/inventory")


# ---------------------------
# ORDERS (scoped to manager's store)
# ---------------------------
@manager_bp.route("/orders")
def orders():
    if session.get("role") not in ("manager", "customer"):
        return redirect("/login")

    db = app.db

    if session.get("role") == "manager":
        store  = get_manager_store()
        loc_id = store.location_id if store else None
        if loc_id:
            all_orders = (
                db.query(CustomerOrder)
                .filter_by(location_id=loc_id)
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
# UPDATE ORDER STATUS (manager only)
# ---------------------------
@manager_bp.route("/orders/update_status", methods=["POST"])
def update_order_status():
    guard = require_manager()
    if guard:
        return guard

    db       = app.db
    store    = get_manager_store()
    loc_id   = store.location_id if store else None
    order_id = request.form.get("order_id")
    new_status = request.form.get("status", "").strip()

    if order_id and new_status:
        q = db.query(CustomerOrder).filter_by(order_id=int(order_id))
        if loc_id:
            q = q.filter_by(location_id=loc_id)   # can't update other stores
        order = q.first()
        if order:
            order.status = new_status
            db.commit()

    return redirect("/orders")


# ---------------------------
# ADD NEW LOCATION (store)
# ---------------------------
@manager_bp.route("/location/add", methods=["GET", "POST"])
def add_location():
    guard = require_manager()
    if guard:
        return guard

    db           = app.db
    error        = None
    success      = False
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

    db           = app.db
    error        = None
    success      = False
    all_stores   = db.query(Store).order_by(Store.location_id).all()
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
        # Refresh after commit
        all_stores = db.query(Store).order_by(Store.location_id).all()

    return render_template(
        "assign_manager.html",
        error=error,
        success=success,
        all_stores=all_stores,
        all_managers=all_managers,
    )


# ---------------------------
# CREATE MANAGER
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
            db.add(Manager(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,   # stored plain to match existing auth
            ))
            db.commit()
            success = True

    return render_template("create_manager.html", error=error, success=success)
