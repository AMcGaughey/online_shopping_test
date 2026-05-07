from flask import current_app as app, Blueprint, render_template, request, redirect, session
from models.book import Book
from models.inventory import Inventory
from models.store import Store
from models.customer_order import CustomerOrder
from models.items_ordered import ItemsOrdered
from models.shipping import Shipping
from datetime import datetime

shop_bp = Blueprint("shop", __name__)


# ---------------------------
# SHOP PAGE
# ---------------------------
@shop_bp.route("/shop")
def shop():
    db = app.db
    books  = db.query(Book).all()
    stores = db.query(Store).order_by(Store.location_id).all()

    # Attach lowest price across all stores (fallback to None if no inventory)
    for book in books:
        inv = (
            db.query(Inventory)
            .filter_by(isbn=book.isbn)
            .order_by(Inventory.price)
            .first()
        )
        book.price = float(inv.price) if inv else None

        # Also attach the list of location_ids where this book is in stock
        stock_locs = (
            db.query(Inventory.location_id)
            .filter(Inventory.isbn == book.isbn, Inventory.quantity > 0)
            .all()
        )
        book.stock_locations = [r[0] for r in stock_locs]

    return render_template("shop.html", books=books, stores=stores)


# ---------------------------
# ADD TO CART
# ---------------------------
@shop_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return redirect("/login")

    isbn = request.form.get("isbn", "").strip()
    if not isbn:
        return redirect("/shop")

    cart = session.get("cart", [])
    cart.append(isbn)
    session["cart"] = cart
    session.modified = True

    return redirect("/shop")


# ---------------------------
# REMOVE FROM CART
# ---------------------------
@shop_bp.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    isbn = request.form.get("isbn", "").strip()
    cart = session.get("cart", [])
    if isbn in cart:
        cart.remove(isbn)
    session["cart"] = cart
    session.modified = True
    return redirect("/cart")


# ---------------------------
# VIEW CART
# ---------------------------
@shop_bp.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect("/login")

    db         = app.db
    cart_items = []
    cart_isbns = session.get("cart", [])

    # Aggregate duplicates
    isbn_counts = {}
    for isbn in cart_isbns:
        isbn_counts[isbn] = isbn_counts.get(isbn, 0) + 1

    for isbn, qty in isbn_counts.items():
        book = db.query(Book).filter_by(isbn=isbn).first()
        if book:
            inv   = db.query(Inventory).filter_by(isbn=isbn).order_by(Inventory.price).first()
            price = float(inv.price) if inv else 10.00
            cart_items.append({
                "isbn":      isbn,
                "title":     book.title,
                "genre":     book.genre,
                "cover":     book.cover_type,
                "publisher": book.publisher.publisher if book.publisher else "—",
                "price":     price,
                "quantity":  qty,
            })

    stores = db.query(Store).order_by(Store.location_id).all()
    return render_template("cart.html", cart=cart_items, stores=stores)


# ---------------------------
# CHECKOUT
# ---------------------------
@shop_bp.route("/checkout", methods=["POST"])
def checkout():
    if "user_id" not in session:
        return redirect("/login")

    db          = app.db
    cart_isbns  = session.get("cart", [])

    if not cart_isbns:
        return redirect("/cart")

    # Pick a location (from form or default to 1)
    try:
        location_id = int(request.form.get("location_id", 1))
    except (ValueError, TypeError):
        location_id = 1

    # Aggregate
    isbn_counts = {}
    for isbn in cart_isbns:
        isbn_counts[isbn] = isbn_counts.get(isbn, 0) + 1

    # Create order
    order = CustomerOrder(
        customer_id=session["user_id"],
        location_id=location_id,
        date=datetime.now(),
        total=0,
        status="Processing",
    )
    db.add(order)
    db.flush()   # get order_id before adding items

    total = 0.0
    for isbn, qty in isbn_counts.items():
        inv   = db.query(Inventory).filter_by(isbn=isbn).order_by(Inventory.price).first()
        price = float(inv.price) if inv else 10.00
        total += price * qty
        db.add(ItemsOrdered(order_id=order.order_id, isbn=isbn, quantity=qty, price=price))

    order.total = round(total, 2)

    # Shipping record
    ship_address = session.get("address", request.form.get("ship_address", "TBD"))
    db.add(Shipping(order_id=order.order_id, date=datetime.now(), address=ship_address))

    db.commit()

    # Clear cart
    session.pop("cart", None)
    session.modified = True

    return redirect("/orders")
