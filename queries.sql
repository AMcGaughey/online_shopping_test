-- Top 20 selling books
SELECT 
    o.location_id,
    i.isbn,
    SUM(i.quantity) AS total_sold
FROM items_ordered i
JOIN customer_order o ON i.order_id = o.order_id
GROUP BY o.location_id, i.isbn
ORDER BY o.location_id, total_sold DESC;

-- Top 20 Selling books per 
SELECT 
    s.location_id,
    i.isbn,
    SUM(i.quantity) AS total_sold
FROM items_ordered i
JOIN customer_order o ON i.order_id = o.order_id
JOIN store s ON o.location_id = s.location_id
GROUP BY s.location_id, i.isbn
ORDER BY s.location_id, total_sold DESC;

-- Top Selling Stores
SELECT 
    location_id,
    SUM(total) AS total_sales
FROM customer_order
WHERE YEAR(date) = YEAR(CURDATE())
GROUP BY location_id
ORDER BY total_sales DESC
LIMIT 5;

-- Top Selling Books
SELECT 
    i.isbn,
    SUM(i.quantity) AS total_sold
FROM items_ordered i
GROUP BY i.isbn
ORDER BY total_sold DESC
LIMIT 20;

-- Most Popular Genres
SELECT 
    b.genre,
    SUM(i.quantity) AS total_sold
FROM items_ordered i
JOIN book b ON i.isbn = b.isbn
GROUP BY b.genre
ORDER BY total_sold DESC;

-- Top Authors
SELECT 
    a.author_first_name,
    a.author_last_name,
    SUM(i.quantity) AS total_sold
FROM items_ordered i
JOIN book b ON i.isbn = b.isbn
JOIN writes w ON b.isbn = w.isbn
JOIN author a ON w.author_id = a.author_id
GROUP BY a.author_id
ORDER BY total_sold DESC;

-- Inventory Levels
SELECT 
    location_id,
    isbn,
    quantity
FROM inventory
ORDER BY location_id, quantity ASC;

-- Low Stock Alerts
SELECT 
    location_id,
    isbn,
    quantity
FROM inventory
WHERE quantity < 5
ORDER BY quantity ASC;

-- Customer Lifetime Value
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(o.total) AS lifetime_value
FROM customer_order o
JOIN customer c ON o.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY lifetime_value DESC;

-- Orders Per Month, Per Stores
SELECT 
    location_id,
    MONTH(date) AS month,
    COUNT(order_id) AS total_orders,
    SUM(total) AS revenue
FROM customer_order
GROUP BY location_id, MONTH(date)
ORDER BY location_id, month;

-- Shipping Performance
SELECT 
    s.shipping_id,
    s.order_id,
    s.date,
    s.address
FROM shipping s
ORDER BY s.date DESC;