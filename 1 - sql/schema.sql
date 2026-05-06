-- Create database
CREATE DATABASE IF NOT EXISTS onlineshopping;
USE onlineshopping;

-- CUSTOMER
CREATE TABLE customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(200),
    password VARCHAR(255)
);

-- PUBLISHER
CREATE TABLE publisher (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    publisher VARCHAR(150),
    email VARCHAR(150),
    phone VARCHAR(20),
    website VARCHAR(255)
);

-- AUTHOR
CREATE TABLE author (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    author_first_name VARCHAR(100),
    author_last_name VARCHAR(100)
);

-- BOOK
CREATE TABLE book (
    isbn VARCHAR(20) PRIMARY KEY,
    publisher_id INT,
    upc VARCHAR(20),
    title VARCHAR(255),
    genre VARCHAR(100),
    cover_type VARCHAR(50),
    release_year INT,
    FOREIGN KEY (publisher_id) REFERENCES publisher(publisher_id)
);

-- WRITES (many-to-many: book ↔ author)
CREATE TABLE writes (
    isbn VARCHAR(20),
    author_id INT,
    PRIMARY KEY (isbn, author_id),
    FOREIGN KEY (isbn) REFERENCES book(isbn),
    FOREIGN KEY (author_id) REFERENCES author(author_id)
);

-- MANAGER
CREATE TABLE manager (
    manager_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    password VARCHAR(255)
);

-- STORE
CREATE TABLE store (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    manager_id INT,
    address VARCHAR(200),
    FOREIGN KEY (manager_id) REFERENCES manager(manager_id)
);

-- INVENTORY
CREATE TABLE inventory (
    location_id INT,
    isbn VARCHAR(20),
    quantity INT,
    price DECIMAL(10,2),
    PRIMARY KEY (location_id, isbn),
    FOREIGN KEY (location_id) REFERENCES store(location_id),
    FOREIGN KEY (isbn) REFERENCES book(isbn)
);

-- CUSTOMER ORDER
CREATE TABLE customer_order (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT,
    customer_id INT,
    date DATETIME,
    total DECIMAL(10,2),
    status VARCHAR(50),
    FOREIGN KEY (location_id) REFERENCES store(location_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

-- ITEMS ORDERED
CREATE TABLE items_ordered (
    order_id INT,
    isbn VARCHAR(20),
    quantity INT,
    price DECIMAL(10,2),
    PRIMARY KEY (order_id, isbn),
    FOREIGN KEY (order_id) REFERENCES customer_order(order_id),
    FOREIGN KEY (isbn) REFERENCES book(isbn)
);

-- SHIPPING
CREATE TABLE shipping (
    shipping_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    date DATETIME,
    address VARCHAR(200),
    FOREIGN KEY (order_id) REFERENCES customer_order(order_id)
);
