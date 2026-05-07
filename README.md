# Bookshelf: A Bookstore Enterprise
## Jump To
[Overview](#overview)\
[Requirements](#requirements)\
[Dependencies](#dependencies)\
[Installation](#installation)\
[Project Structure](#project-structure)\
[Final Notes](#final-notes)
## Overview
Based on a bookstore, this project replicates an inventory system to track books, authors, publishers, inventory, management, 
locations, orders, and shipments. 
There are two main user roles: 
1. Customer - can browse the catalog and place orders.
2. Manager - Manages inventory, order statuses, store locations, and other manager profiles. 
## Requirements
- python 3.11
- MySQL 8.0
- Visual Studio Code
- Extension: MySQL - Database Client
### Dependencies
1. Flask - Python web framework tool
2. SQLAlchemy - Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL
3. Faker - Fake Data Generation
## Installation
1. Open Repository
2. Configure The Database
   In config.py, update user, password, and secret key
    ```
    DB_USER = "shopuser"
    DB_PASSWORD = "12345"
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_NAME = "onlineshopping"

    SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SECRET_KEY = "dev-secret-key"
    ```

   Within MySQL create a new SQL connection. Within the first query insert:
   ```
   CREATE DATABASE onlineshopping;
   CREATE USER 'shopuser'@'localhost' IDENTIFIED BY '12345';
   GRANT ALL PRIVILEGES ON onlineshopping.* TO 'shopuser'@'localhost';
   FLUSH PRIVILEGES;
   ```
  Create a new schema and copy/paste in schema.sql\
  Use mysql-connector and sqlalchemy to connect to visual studios
  and MySQL extension to visualize the database through VS Code. 

4. Install Dependencies
   ``` 
   pip install flask
   pip install mysql-connector
   pip install sqlalchemy
   pip install pymysql
   pip install werkzeug
   pip install faker
   ```
5. Generate Fake data or use prefilled generated_data.sql from project.
   Open SQL files through MySQL and excute.
7. Run the application
   ```
   python app.py
   ```
## Project Structure 
app.py: DB, Flask, and Blueprint setup\
config.py DB credentials\
manager_password_hash.py
##### routes
  --auth.py: login, logout, register users\
  --shop.py: browse, cart, checkout\
--manager.py: dashboard, inventory, orders, locations
##### models: SQLAlchemy Models
--base.py\
--book.py\
--customer.py\
--customer_order.py\
--inventory.py\
--items_ordered.py\
--manager.py\
--shipping.py\
--store.py\
--writes.py
##### templates: HTML frontend
--add_inventory.html\
--add_location.html\
--assign_manager.html\
--cart.html\
--inventory.html\
--layout.html\
--login.html\
--manager_dashboard.html\
--orders.html\
--register.html\
--shipping.html\
--shop.html
##### static: UI themes
--styles.css
##### data_generation
-- generate_data.py
## Final Notes
#### Limitations
-	No pagination on the shop, inventory, or orders pages — large datasets will slow render time.
-	Cart state is stored in the Flask session cookie and is lost on logout.
-	Inventory quantities are not decremented when an order is placed.
-	The SECRET_KEY in config.py is hardcoded — replace with an environment variable for any non-local deployment
#### Project Future
- Image Support for book covers
- Display more book information (summary, reviews, etc.)
- Integrate Payment processing
  
