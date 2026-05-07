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

    # All books with lowest price across all stores
    books  = db.query(Book).all()
    stores = db.query(Store).all()

    for book in books:
        inv = (
            db.query(Inventory)
            .filter_by(isbn=book.isbn)
            .order_by(Inventory.price)
            .first()
        )
        book.price = float(inv.price) if inv else None

    return render_template("shop.html", books=books, stores=stores)


# ---------------------------
# ADD TO CART
# ---------------------------
@shop_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return redirect("/login")

    isbn = request.form["isbn"]

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(isbn)
    session.modified = True

    return redirect("/shop")


# ---------------------------
# VIEW CART
# ---------------------------
@shop_bp.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect("/login")

    db         = app.db
    cart_items = []

    if "cart" in session:
        isbn_counts = {}
        for isbn in session["cart"]:
            isbn_counts[isbn] = isbn_counts.get(isbn, 0) + 1

        for isbn, qty in isbn_counts.items():
            book = db.query(Book).filter_by(isbn=isbn).first()
            if book:
                inv   = db.query(Inventory).filter_by(isbn=isbn).first()
                price = float(inv.price) if inv else 10.00
                cart_items.append({
                    "isbn":     isbn,
                    "title":    book.title,
                    "genre":    book.genre,
                    "price":    price,
                    "quantity": qty,
                })

    return render_template("cart.html", cart=cart_items)


# ---------------------------
# CHECKOUT
# ---------------------------
@shop_bp.route("/checkout", methods=["POST"])
def checkout():
    if "user_id" not in session:
        return redirect("/login")

    db          = app.db
    address     = request.form.get("address", "")
    location_id = int(request.form.get("location_id", 1))

    if "cart" not in session or not session["cart"]:
        return redirect("/cart")

    isbn_counts = {}
    for isbn in session["cart"]:
        isbn_counts[isbn] = isbn_counts.get(isbn, 0) + 1

    order = CustomerOrder(
        location_id=location_id,
        customer_id=session["user_id"],
        date=datetime.now(),
        total=0,
        status="processing",
    )
    db.add(order)
    db.flush()

    total = 0.0
    for isbn, qty in isbn_counts.items():
        inv   = db.query(Inventory).filter_by(isbn=isbn).first()
        price = float(inv.price) if inv else 10.00
        item  = ItemsOrdered(order_id=order.order_id, isbn=isbn, quantity=qty, price=price)
        db.add(item)
        total += price * qty

    order.total = round(total, 2)

    ship = Shipping(order_id=order.order_id, date=datetime.now(), address=address)
    db.add(ship)
    db.commit()

    session.pop("cart", None)
    session.modified = True

    return redirect("/orders")
