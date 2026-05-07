from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker("en_US")

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
NUM_CUSTOMERS   = 40
NUM_MANAGERS    = 8
NUM_PUBLISHERS  = 12
NUM_AUTHORS     = 40
NUM_BOOKS       = 120          # 8 books × 15 genres = 120 exactly
NUM_ORDERS      = 150

GENRES = [
    "Fantasy", "Science Fiction", "Romance", "Mystery", "Thriller",
    "Non-fiction", "Biography", "History", "Horror", "Young Adult",
    "Literary Fiction", "Self-Help", "Graphic Novel", "Children's",
    "True Crime",
]

COVER_TYPES = ["Hardcover", "Paperback", "Ebook"]

# Real US city-based store locations
STORE_LOCATIONS = [
    {"city": "Austin",    "state": "TX", "address": "1204 South Congress Ave, Austin, TX 78704"},
    {"city": "Nashville", "state": "TN", "address": "305 Broadway, Nashville, TN 37201"},
    {"city": "Portland",  "state": "OR", "address": "820 NW 23rd Ave, Portland, OR 97210"},
    {"city": "Denver",    "state": "CO", "address": "1515 Market St, Denver, CO 80202"},
    {"city": "Atlanta",   "state": "GA", "address": "675 Ponce De Leon Ave NE, Atlanta, GA 30308"},
    {"city": "Seattle",   "state": "WA", "address": "1521 Pike Pl, Seattle, WA 98101"},
    {"city": "Chicago",   "state": "IL", "address": "57 W Grand Ave, Chicago, IL 60654"},
    {"city": "Boston",    "state": "MA", "address": "206 Newbury St, Boston, MA 02116"},
]

NUM_STORES = len(STORE_LOCATIONS)   # 8


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def us_phone():
    return fake.numerify("(###) ###-####")

def random_date(days_back=365):
    return datetime.now() - timedelta(days=random.randint(0, days_back))

def gen_password():
    return fake.numerify("##########")

def esc(s):
    """Escape single quotes for SQL."""
    return str(s).replace("'", "''")


# ─────────────────────────────────────────────────────────────
# CUSTOMER
# ─────────────────────────────────────────────────────────────
def generate_customers():
    rows = []
    for _ in range(NUM_CUSTOMERS):
        first    = fake.first_name()
        last     = fake.last_name()
        email    = fake.unique.email()
        phone    = us_phone()
        address  = esc(fake.address().replace("\n", ", "))
        password = gen_password()
        rows.append(
            f"INSERT INTO customer(first_name, last_name, email, phone, address, password) "
            f"VALUES ('{esc(first)}', '{esc(last)}', '{email}', '{phone}', '{address}', '{password}');"
        )
    return rows


# ─────────────────────────────────────────────────────────────
# MANAGER
# ─────────────────────────────────────────────────────────────
def generate_managers():
    rows = []
    for _ in range(NUM_MANAGERS):
        first    = fake.first_name()
        last     = fake.last_name()
        email    = fake.unique.email()
        password = gen_password()
        rows.append(
            f"INSERT INTO manager(first_name, last_name, email, password) "
            f"VALUES ('{esc(first)}', '{esc(last)}', '{email}', '{password}');"
        )
    return rows


# ─────────────────────────────────────────────────────────────
# PUBLISHER
# ─────────────────────────────────────────────────────────────
def generate_publishers():
    rows = []
    for _ in range(NUM_PUBLISHERS):
        name    = esc(fake.company())
        email   = fake.company_email()
        phone   = us_phone()
        website = fake.url()
        rows.append(
            f"INSERT INTO publisher(publisher, email, phone, website) "
            f"VALUES ('{name}', '{email}', '{phone}', '{website}');"
        )
    return rows


# ─────────────────────────────────────────────────────────────
# AUTHOR
# ─────────────────────────────────────────────────────────────
def generate_authors():
    rows = []
    for _ in range(NUM_AUTHORS):
        first = fake.first_name()
        last  = fake.last_name()
        rows.append(
            f"INSERT INTO author(author_first_name, author_last_name) "
            f"VALUES ('{esc(first)}', '{esc(last)}');"
        )
    return rows


# ─────────────────────────────────────────────────────────────
# BOOK  — guaranteed even coverage of every genre
# ─────────────────────────────────────────────────────────────
def generate_books():
    rows = []

    # Build a pool so every genre appears exactly NUM_BOOKS/len(GENRES) times
    # (120 books ÷ 15 genres = 8 each, perfectly even)
    genre_pool = []
    base      = NUM_BOOKS // len(GENRES)
    remainder = NUM_BOOKS % len(GENRES)
    for i, g in enumerate(GENRES):
        genre_pool.extend([g] * (base + (1 if i < remainder else 0)))
    random.shuffle(genre_pool)

    for genre in genre_pool:
        isbn         = fake.isbn13()
        upc          = fake.ean13()
        title        = esc(fake.sentence(nb_words=random.randint(2, 5)).rstrip("."))
        cover        = random.choice(COVER_TYPES)
        year         = random.randint(1975, 2024)
        publisher_id = random.randint(1, NUM_PUBLISHERS)
        rows.append(
            f"INSERT INTO book(isbn, publisher_id, upc, title, genre, cover_type, release_year) "
            f"VALUES ('{isbn}', {publisher_id}, '{upc}', '{title}', '{genre}', '{cover}', {year});"
        )
    return rows


# ─────────────────────────────────────────────────────────────
# WRITES
# ─────────────────────────────────────────────────────────────
def generate_writes():
    rows = []
    for book_index in range(NUM_BOOKS):
        num_authors = random.randint(1, 2)
        author_ids  = random.sample(range(1, NUM_AUTHORS + 1), num_authors)
        for aid in author_ids:
            rows.append(
                f"INSERT INTO writes(isbn, author_id) "
                f"VALUES ((SELECT isbn FROM book LIMIT {book_index},1), {aid});"
            )
    return rows


# ─────────────────────────────────────────────────────────────
# STORE  — real US city addresses, one manager per store
# ─────────────────────────────────────────────────────────────
def generate_stores():
    rows = []
    # Assign each store a unique manager (shuffle manager IDs)
    manager_ids = list(range(1, NUM_MANAGERS + 1))
    random.shuffle(manager_ids)

    for store_id, loc in enumerate(STORE_LOCATIONS, start=1):
        manager_id = manager_ids[store_id - 1]
        address    = esc(loc["address"])
        rows.append(
            f"INSERT INTO store(location_id, manager_id, address) "
            f"VALUES ({store_id}, {manager_id}, '{address}');"
        )
    return rows


# ─────────────────────────────────────────────────────────────
# INVENTORY
# ─────────────────────────────────────────────────────────────
def generate_inventory():
    rows = []
    for store_id in range(1, NUM_STORES + 1):
        for book_index in range(NUM_BOOKS):
            isbn_query = f"(SELECT isbn FROM book LIMIT {book_index},1)"
            qty   = random.randint(0, 50)
            price = round(random.uniform(5, 45), 2)
            rows.append(
                f"INSERT INTO inventory(location_id, isbn, quantity, price) "
                f"VALUES ({store_id}, {isbn_query}, {qty}, {price});"
            )
    return rows


# ─────────────────────────────────────────────────────────────
# ORDERS + ITEMS + SHIPPING
# ─────────────────────────────────────────────────────────────
def generate_orders_items_shipping():
    orders   = []
    items    = []
    shipping = []

    for order_id in range(1, NUM_ORDERS + 1):
        customer_id = random.randint(1, NUM_CUSTOMERS)
        location_id = random.randint(1, NUM_STORES)
        date        = random_date().strftime("%Y-%m-%d %H:%M:%S")
        status      = random.choice(["processing", "shipped", "delivered"])

        orders.append(
            f"INSERT INTO customer_order(location_id, customer_id, date, total, status) "
            f"VALUES ({location_id}, {customer_id}, '{date}', 0, '{status}');"
        )

        num_items   = random.randint(1, 5)
        book_idxs   = random.sample(range(NUM_BOOKS), num_items)
        order_total = 0.0

        for idx in book_idxs:
            qty   = random.randint(1, 3)
            price = round(random.uniform(5, 45), 2)
            order_total += qty * price
            items.append(
                f"INSERT INTO items_ordered(order_id, isbn, quantity, price) "
                f"VALUES ({order_id}, (SELECT isbn FROM book LIMIT {idx},1), {qty}, {price});"
            )

        orders.append(
            f"UPDATE customer_order SET total = {round(order_total, 2)} WHERE order_id = {order_id};"
        )

        if status in ("shipped", "delivered"):
            ship_dt   = (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") +
                         timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S")
            ship_addr = esc(fake.address().replace("\n", ", "))
            shipping.append(
                f"INSERT INTO shipping(order_id, date, address) "
                f"VALUES ({order_id}, '{ship_dt}', '{ship_addr}');"
            )

    return orders, items, shipping


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    sections = [
        ("-- CUSTOMERS",  generate_customers()),
        ("-- MANAGERS",   generate_managers()),
        ("-- PUBLISHERS", generate_publishers()),
        ("-- AUTHORS",    generate_authors()),
        ("-- BOOKS",      generate_books()),
        ("-- WRITES",     generate_writes()),
        ("-- STORES",     generate_stores()),
        ("-- INVENTORY",  generate_inventory()),
    ]

    orders, items, ship = generate_orders_items_shipping()
    sections += [
        ("-- ORDERS",   orders),
        ("-- ITEMS",    items),
        ("-- SHIPPING", ship),
    ]

    lines = ["USE onlineshopping;", ""]
    for header, rows in sections:
        lines.append(header)
        lines.extend(rows)
        lines.append("")

    with open("generated_data.sql", "w") as f:
        f.write("\n".join(lines))

    print("✓ generated_data.sql written")
    print(f"  Books   : {NUM_BOOKS}  ({len(GENRES)} genres, {NUM_BOOKS // len(GENRES)} each)")
    print(f"  Stores  : {NUM_STORES}  (real US city addresses)")
    print(f"  Managers: {NUM_MANAGERS}  (one per store)")
    print(f"  Inventory: {NUM_BOOKS * NUM_STORES} records")


if __name__ == "__main__":
    main()
