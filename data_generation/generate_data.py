import csv
import random
from faker import Faker
from datetime import datetime
from werkzeug.security import generate_password_hash

fake = Faker("en_US")   # US-style phone numbers, addresses, names


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def us_phone():
    return fake.numerify("(###) ###-####")

def clean_email(first, last):
    base = f"{first.lower()}.{last.lower()}"
    domain = fake.free_email_domain()
    return f"{base}@{domain}"

def sql_escape(value):
    """Escape single quotes for SQL."""
    if isinstance(value, str):
        return value.replace("'", "''")
    return value


# ---------------------------------------------------------
# CSV Writer
# ---------------------------------------------------------

def write_csv(filename, fieldnames, rows):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------
# SQL Writer
# ---------------------------------------------------------

def write_sql(filename, table, rows):
    with open(filename, "w", encoding="utf-8") as f:
        for row in rows:
            columns = ", ".join(row.keys())
            values = []

            for v in row.values():
                if v is None:
                    values.append("NULL")
                elif isinstance(v, (int, float)):
                    values.append(str(v))
                else:
                    values.append(f"'{sql_escape(str(v))}'")

            values_str = ", ".join(values)
            f.write(f"INSERT INTO {table} ({columns}) VALUES ({values_str});\n")


# ---------------------------------------------------------
# Data Generators
# ---------------------------------------------------------

def generate_customers(n=50):
    customers = []
    for cid in range(1, n + 1):
        first = fake.first_name()
        last = fake.last_name()
        customers.append({
            "customer_id": cid,
            "first_name": first,
            "last_name": last,
            "email": clean_email(first, last),
            "phone": us_phone(),
            "address": fake.address().replace("\n", ", "),
            "password": generate_password_hash(fake.password())
        })
    return customers


def generate_publishers(n=10):
    publishers = []
    for pid in range(1, n + 1):
        name = fake.company()
        publishers.append({
            "publisher_id": pid,
            "publisher": name,
            "email": clean_email(name.replace(" ", ""), "pub"),
            "phone": us_phone(),
            "website": fake.url()
        })
    return publishers


def generate_authors(n=30):
    authors = []
    for aid in range(1, n + 1):
        first = fake.first_name()
        last = fake.last_name()
        authors.append({
            "author_id": aid,
            "author_first_name": first,
            "author_last_name": last
        })
    return authors


def generate_books(n=40, publishers=None):
    books = []
    for i in range(n):
        isbn = fake.isbn13(separator="")
        books.append({
            "isbn": isbn,
            "publisher_id": random.choice(publishers)["publisher_id"],
            "upc": fake.ean13(),
            "title": fake.sentence(nb_words=4).replace(".", ""),
            "genre": random.choice(["Fiction", "Sci-Fi", "Romance", "Mystery", "Fantasy", "Nonfiction"]),
            "cover_type": random.choice(["Hardcover", "Paperback"]),
            "release_year": random.randint(1990, 2024)
        })
    return books


def generate_writes(books, authors):
    writes = []
    for book in books:
        for _ in range(random.randint(1, 3)):
            writes.append({
                "isbn": book["isbn"],
                "author_id": random.choice(authors)["author_id"]
            })
    return writes


def generate_managers(n=5):
    managers = []
    for mid in range(1, n + 1):
        first = fake.first_name()
        last = fake.last_name()
        managers.append({
            "manager_id": mid,
            "first_name": first,
            "last_name": last,
            "email": clean_email(first, last),
            "password": fake.password()
        })
    return managers


def generate_stores(managers):
    stores = []
    for m in managers:
        stores.append({
            "location_id": m["manager_id"],
            "manager_id": m["manager_id"],
            "address": fake.address().replace("\n", ", ")
        })
    return stores


def generate_inventory(stores, books):
    inventory = []
    for store in stores:
        for book in random.sample(books, 20):
            inventory.append({
                "location_id": store["location_id"],
                "isbn": book["isbn"],
                "quantity": random.randint(1, 50),
                "price": round(random.uniform(5, 40), 2)
            })
    return inventory


def generate_orders(customers, stores, books, n=60):
    orders = []
    items = []
    shipping = []

    for oid in range(1, n + 1):
        customer = random.choice(customers)
        store = random.choice(stores)

        orders.append({
            "order_id": oid,
            "location_id": store["location_id"],
            "customer_id": customer["customer_id"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": 0,
            "status": random.choice(["Processing", "Shipped", "Delivered"])
        })

        order_total = 0
        for _ in range(random.randint(1, 5)):
            book = random.choice(books)
            price = round(random.uniform(5, 40), 2)
            qty = random.randint(1, 3)

            items.append({
                "order_id": oid,
                "isbn": book["isbn"],
                "quantity": qty,
                "price": price
            })

            order_total += price * qty

        orders[-1]["total"] = round(order_total, 2)

        shipping.append({
            "shipping_id": oid,
            "order_id": oid,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "address": fake.address().replace("\n", ", ")
        })

    return orders, items, shipping


# ---------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------

def main():
    customers = generate_customers()
    publishers = generate_publishers()
    authors = generate_authors()
    books = generate_books(publishers=publishers)
    writes = generate_writes(books, authors)
    managers = generate_managers()
    stores = generate_stores(managers)
    inventory = generate_inventory(stores, books)
    orders, items, shipping = generate_orders(customers, stores, books)

    datasets = {
        "customers": customers,
        "publishers": publishers,
        "authors": authors,
        "books": books,
        "writes": writes,
        "managers": managers,
        "stores": stores,
        "inventory": inventory,
        "orders": orders,
        "items_ordered": items,
        "shipping": shipping
    }

    for name, rows in datasets.items():
        write_csv(f"{name}.csv", rows[0].keys(), rows)
        write_sql(f"{name}.sql", name, rows)

    print("CSV and SQL files generated successfully!")


if __name__ == "__main__":
    main()
