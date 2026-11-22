USE stocksync_db;

-- Seed data: Five StockSync stores
-- IDs match the existing inventory references.

INSERT INTO stores (store_id, store_name, address, city)
VALUES
(4, 'StockSync Hatfield', '1122 Burnett Street', 'Pretoria'),
(5, 'StockSync Menlyn Maine', '180 Amarand Ave', 'Pretoria'),
(6, 'StockSync The Grove', 'The Grove Mall', 'Pretoria'),
(7, 'StockSync Hillcrest', 'Hillcrest Boulevard Shopping Centre', 'Pretoria'),
(8, 'StockSync Equestria', 'Simon Vermooten Rd', 'Pretoria')
ON DUPLICATE KEY UPDATE
    store_name = VALUES(store_name),
    address = VALUES(address),
    city = VALUES(city);


-- Seed data: Five product categories

INSERT INTO categories (category_id, category_name, description)
VALUES
(1, 'Groceries', 'Everyday essentials and household products'),
(2, 'Beverages', 'Water, juices and soft drinks'),
(3, 'Personal Care', 'Personal hygiene care products'),
(4, 'Household', 'Household cleaning and maintenance products'),
(5, 'Snacks', 'Chips, biscuits and treats')
ON DUPLICATE KEY UPDATE
    category_name = VALUES(category_name),
    description = VALUES(description);


-- Seed data: Seven StockSync products

INSERT INTO products
(product_id, product_name, sku, category_id, unit_price, description)
VALUES
(1, 'Rice 2kg', 'GRO001', 1, 49.99, 'White rice 2kg'),
(2, 'Milk 1L', 'GRO002', 1, 19.99, 'Fresh milk'),
(3, 'Coca-Cola 2L', 'BEV001', 2, 24.99, 'Soft drink'),
(4, 'Orange Juice 1L', 'BEV002', 2, 29.99, 'Orange juice'),
(5, 'Toothpaste', 'PER001', 3, 22.99, 'Toothpaste 100ml'),
(6, 'Dishwashing Liquid', 'HOU001', 4, 34.99, 'Dishwashing liquid 750ml'),
(7, 'Potato Chips', 'SNA001', 5, 17.99, 'Salted potato chips')
ON DUPLICATE KEY UPDATE
    product_name = VALUES(product_name),
    sku = VALUES(sku),
    category_id = VALUES(category_id),
    unit_price = VALUES(unit_price),
    description = VALUES(description);


-- Seed data: Inventory for StockSync stores
-- Existing inventory records shown in MySQL Workbench

INSERT INTO inventory
(inventory_id, store_id, product_id, quantity_on_hand, reorder_level)
VALUES
-- StockSync Hatfield
(1, 4, 1, 130, 20),
(2, 4, 2, 80, 15),
(3, 4, 3, 120, 25),
(4, 4, 4, 60, 15),
(5, 4, 5, 45, 10),
(6, 4, 6, 35, 10),
(7, 4, 7, 90, 20),

-- StockSync Menlyn Maine
(8, 5, 1, 75, 20),
(9, 5, 2, 50, 15),
(10, 5, 3, 100, 25),
(11, 5, 4, 40, 15),
(12, 5, 5, 30, 10),
(13, 5, 6, 25, 10),
(14, 5, 7, 65, 20),

-- StockSync The Grove
(15, 6, 1, 55, 20),
(16, 6, 2, 35, 15),
(17, 6, 3, 80, 25),
(18, 6, 4, 25, 15),
(19, 6, 5, 20, 10),
(20, 6, 6, 15, 10),
(21, 6, 7, 45, 20)
ON DUPLICATE KEY UPDATE
    store_id = VALUES(store_id),
    product_id = VALUES(product_id),
    quantity_on_hand = VALUES(quantity_on_hand),
    reorder_level = VALUES(reorder_level);


-- Inventory for StockSync Hillcrest (Store 7)
-- and StockSync Equestria (Store 8)

INSERT INTO inventory
    (store_id, product_id, quantity_on_hand, reorder_level)
VALUES
-- StockSync Hillcrest
(7, 1, 95, 20),
(7, 2, 60, 15),
(7, 3, 110, 25),
(7, 4, 45, 15),
(7, 5, 30, 10),
(7, 6, 20, 10),
(7, 7, 70, 20),

-- StockSync Equestria
(8, 1, 85, 20),
(8, 2, 55, 15),
(8, 3, 90, 25),
(8, 4, 40, 15),
(8, 5, 25, 10),
(8, 6, 18, 10),
(8, 7, 60, 20)

ON DUPLICATE KEY UPDATE
    quantity_on_hand = VALUES(quantity_on_hand),
    reorder_level = VALUES(reorder_level);
