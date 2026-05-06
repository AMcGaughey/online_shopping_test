from flask import current_app as app,Blueprint, render_template, request, redirect, session
from models.book import Book
from models.customer_order import CustomerOrder
from models.items_ordered import ItemsOrdered
from datetime import datetime

shop_bp = Blueprint("shop", __name__)

# ---------------------------
# SHOP PAGE
# ---------------------------
@shop_bp.route("/shop")
def shop():
    db = app.db
    books = db.query(Book).all()
    return render_template("shop.html", books=books)


# ---------------------------
# ADD TO CART
# ---------------------------
@shop_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():
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
    db = app.db
    cart_items = []

    if "cart" in session:
        for isbn in session["cart"]:
            book = db.query(Book).filter_by(isbn=isbn).first()
            cart_items.append({
                "title": book.title,
                "price": 10.00,  # placeholder
                "quantity": 1
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

    order = CustomerOrder(
        customer_id=session["user_id"],
        location_id=1,
        date=datetime.now(),
        total=0,
        status="Processing"
    )

    db.add(order)
    db.commit()

    # Add items
    for isbn in session.get("cart", []):
        item = ItemsOrdered(
            order_id=order.order_id,
            isbn=isbn,
            quantity=1,
            price=10.00
        )
        db.add(item)

    db.commit()

    session["cart"] = []
    return redirect("/shop")
