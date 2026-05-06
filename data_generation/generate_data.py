"""
Realistic Data Generator for onlineshopping Database
Matches EXACTLY the schema provided by Alyssa.

Generates:
- customer
- manager
- publisher
- author
- book
- writes
- store
- inventory
- customer_order
- items_ordered
- shipping

Outputs: generated_data.sql
"""

from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker("en_US")  # ensures clean US phone numbers

# -----------------------------
# CONFIGURATION
# -----------------------------
NUM_CUSTOMERS = 40
NUM_MANAGERS = 5
NUM_PUBLISHERS = 10
NUM_AUTHORS = 30
NUM_BOOKS = 60
NUM_STORES = 3
NUM_ORDERS = 120

GENRES = [
    "Fantasy", "Science Fiction", "Romance", "Mystery", "Thriller",
    "Non-fiction", "Biography", "History", "Horror", "Young Adult"
]

COVER_TYPES = ["Hardcover", "Paperback", "Ebook"]


# -----------------------------
# HELPERS
# -----------------------------
def us_phone():
    """Generate a clean US phone number."""
    return fake.numerify("(###) ###-####")


def random_date(days_back=365):
    """Random datetime within the last year."""
    return datetime.now() - timedelta(days=random.randint(0, days_back))

def gen_password():
    return fake.numerify("##########")


# -----------------------------
# CUSTOMER
# -----------------------------
def generate_customers():
    rows = []
    for _ in range(NUM_CUSTOMERS):
        first = fake.first_name()
        last = fake.last_name()
        email = fake.unique.email()
        phone = us_phone()
        address = fake.address().replace("\n", ", ")
        password = gen_password()

        rows.append(
            f"INSERT INTO customer(first_name, last_name, email, phone, address, password) "
            f"VALUES ('{first}', '{last}', '{email}', '{phone}', '{address}', '{password}');"
        )
    return rows


# -----------------------------
# MANAGER
# -----------------------------
def generate_managers():
    rows = []
    for _ in range(NUM_MANAGERS):
        first = fake.first_name()
        last = fake.last_name()
        email = fake.unique.email()
        password = gen_password()

        rows.append(
            f"INSERT INTO manager(first_name, last_name, email, password) "
            f"VALUES ('{first}', '{last}', '{email}', '{password}');"
        )
    return rows


# -----------------------------
# PUBLISHER
# -----------------------------
def generate_publishers():
    rows = []
    for _ in range(NUM_PUBLISHERS):
        name = fake.company().replace("'", "")
        email = fake.company_email()
        phone = us_phone()
        website = fake.url()

        rows.append(
            f"INSERT INTO publisher(publisher, email, phone, website) "
            f"VALUES ('{name}', '{email}', '{phone}', '{website}');"
        )
    return rows


# -----------------------------
# AUTHOR
# -----------------------------
def generate_authors():
    rows = []
    for _ in range(NUM_AUTHORS):
        first = fake.first_name()
        last = fake.last_name()

        rows.append(
            f"INSERT INTO author(author_first_name, author_last_name) "
            f"VALUES ('{first}', '{last}');"
        )
    return rows


# -----------------------------
# BOOK
# -----------------------------
def generate_books():
    rows = []
    for _ in range(NUM_BOOKS):
        isbn = fake.isbn13()
        upc = fake.ean13()
        title = fake.sentence(nb_words=4).replace("'", "")
        genre = random.choice(GENRES)
        cover = random.choice(COVER_TYPES)
        year = random.randint(1980, 2024)
        publisher_id = random.randint(1, NUM_PUBLISHERS)

        rows.append(
            f"INSERT INTO book(isbn, publisher_id, upc, title, genre, cover_type, release_year) "
            f"VALUES ('{isbn}', {publisher_id}, '{upc}', '{title}', '{genre}', '{cover}', {year});"
        )
    return rows


# -----------------------------
# WRITES (book-author relationship)
# -----------------------------
def generate_writes():
    rows = []
    for book_index in range(NUM_BOOKS):
        num_authors = random.randint(1, 3)
        for _ in range(num_authors):
            author_id = random.randint(1, NUM_AUTHORS)
            rows.append(
                f"INSERT INTO writes(isbn, author_id) "
                f"VALUES ((SELECT isbn FROM book LIMIT {book_index},1), {author_id});"
            )
    return rows


# -----------------------------
# STORE
# -----------------------------
def generate_stores():
    rows = []
    for store_id in range(1, NUM_STORES + 1):
        manager_id = random.randint(1, NUM_MANAGERS)
        address = fake.address().replace("\n", ", ")

        rows.append(
            f"INSERT INTO store(location_id, manager_id, address) "
            f"VALUES ({store_id}, {manager_id}, '{address}');"
        )
    return rows


# -----------------------------
# INVENTORY
# -----------------------------
def generate_inventory():
    rows = []
    for store_id in range(1, NUM_STORES + 1):
        for book_index in range(NUM_BOOKS):
            isbn_query = f"(SELECT isbn FROM book LIMIT {book_index},1)"
            qty = random.randint(0, 50)
            price = round(random.uniform(5, 40), 2)

            rows.append(
                f"INSERT INTO inventory(location_id, isbn, quantity, price) "
                f"VALUES ({store_id}, {isbn_query}, {qty}, {price});"
            )
    return rows


# -----------------------------
# ORDERS + ITEMS + SHIPPING
# -----------------------------
def generate_orders_items_shipping():
    orders = []
    items = []
    shipping = []

    for order_id in range(1, NUM_ORDERS + 1):
        customer_id = random.randint(1, NUM_CUSTOMERS)
        location_id = random.randint(1, NUM_STORES)
        date = random_date().strftime("%Y-%m-%d %H:%M:%S")
        status = random.choice(["processing", "shipped", "delivered"])

        orders.append(
            f"INSERT INTO customer_order(location_id, customer_id, date, total, status) "
            f"VALUES ({location_id}, {customer_id}, '{date}', 0, '{status}');"
        )

        # Items
        num_items = random.randint(1, 5)
        total_price = 0

        for _ in range(num_items):
            book_index = random.randint(0, NUM_BOOKS - 1)
            isbn_query = f"(SELECT isbn FROM book LIMIT {book_index},1)"
            qty = random.randint(1, 3)
            price = round(random.uniform(5, 40), 2)
            total_price += price * qty

            items.append(
                f"INSERT INTO items_ordered(order_id, isbn, quantity, price) "
                f"VALUES ({order_id}, {isbn_query}, {qty}, {price});"
            )

        # Update total
        orders.append(
            f"UPDATE customer_order SET total = {round(total_price, 2)} WHERE order_id = {order_id};"
        )

        # Shipping
        ship_date = random_date().strftime("%Y-%m-%d %H:%M:%S")
        address = fake.address().replace("\n", ", ")

        shipping.append(
            f"INSERT INTO shipping(order_id, date, address) "
            f"VALUES ({order_id}, '{ship_date}', '{address}');"
        )

    return orders, items, shipping


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("Generating realistic SQL data...")

    sql = []
    sql += generate_customers()
    sql += generate_managers()
    sql += generate_publishers()
    sql += generate_authors()
    sql += generate_books()
    sql += generate_writes()
    sql += generate_stores()
    sql += generate_inventory()

    orders, items, shipping = generate_orders_items_shipping()
    sql += orders
    sql += items
    sql += shipping

    with open("generated_data.sql", "w", encoding="utf-8") as f:
        for line in sql:
            f.write(line + "\n")

    print("Done! File saved as generated_data.sql")
