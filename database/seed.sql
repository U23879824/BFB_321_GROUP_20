
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
