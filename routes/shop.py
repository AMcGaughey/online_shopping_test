from flask import current_app as app, Blueprint, render_template, request, redirect, session
from models.book import Book
from models.inventory import Inventory
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
    books = db.query(Book).all()

    # Attach a price to each book from inventory (use min price across stores)
    for book in books:
        inv = db.query(Inventory).filter_by(isbn=book.isbn).first()
        book.price = float(inv.price) if inv else None

    return render_template("shop.html", books=books)


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

    db = app.db
    cart_items = []

    if "cart" in session:
        # Aggregate duplicates
        isbn_counts = {}
        for isbn in session["cart"]:
            isbn_counts[isbn] = isbn_counts.get(isbn, 0) + 1

        for isbn, qty in isbn_counts.items():
            book = db.query(Book).filter_by(isbn=isbn).first()
            if book:
                inv = db.query(Inventory).filter_by(isbn=isbn).first()
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
    db = app.db

    if "user_id" not in session:
        return redirect("/login")

    # Build order total
    total = 0.0
    isbn_counts = {}
    for isbn in session.get("cart", []):
        isbn_counts[isbn] = isbn_counts.get(isbn, 0) + 1

    order = CustomerOrder(
        customer_id=session["user_id"],
        location_id=1,
        date=datetime.now(),
        total=0,
        status="Processing"
    )
    db.add(order)
    db.flush()  # get order_id

    for isbn, qty in isbn_counts.items():
        inv = db.query(Inventory).filter_by(isbn=isbn).first()
        price = float(inv.price) if inv else 10.00
        total += price * qty

        item = ItemsOrdered(
            order_id=order.order_id,
            isbn=isbn,
            quantity=qty,
            price=price
        )
        db.add(item)

    order.total = round(total, 2)

    # Create a shipping record
    customer_address = session.get("address", "TBD")
    ship = Shipping(
        order_id=order.order_id,
        date=datetime.now(),
        address=customer_address
    )
    db.add(ship)

    db.commit()
    session["cart"] = []
    return redirect("/orders")
