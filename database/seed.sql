-- database/seed.sql
--
-- Reference copy of the sample data already live in your Supabase
-- project. Do NOT re-run this against your current database - the
-- UNIQUE constraints on email, sku, slug, code, etc. will reject
-- duplicate inserts and the whole script will fail partway through.
--
-- Only run this against a FRESH database (e.g. a new Supabase project
-- created from schema.sql) if you need to reproduce this exact demo
-- dataset.

INSERT INTO categories (name, image) VALUES
('Men', '/images/categories/men.jpg'),
('Women', '/images/categories/women.jpg'),
('Kids', '/images/categories/kids.jpg'),
('Electronics', '/images/categories/electronics.jpg'),
('Footwear', '/images/categories/footwear.jpg'),
('Accessories', '/images/categories/accessories.jpg'),
('Beauty', '/images/categories/beauty.jpg');

INSERT INTO users (id, full_name, email, phone, password_hash, address, city, role) VALUES
('11111111-1111-1111-1111-111111111111','Ali Khan','ali@example.com','03001234567','hashed123','Block A Gulshan','Karachi','customer'),
('22222222-2222-2222-2222-222222222222','Sara Ahmed','sara@example.com','03011234567','hashed123','Johar','Karachi','customer'),
('33333333-3333-3333-3333-333333333333','Usman Tariq','usman@example.com','03121234567','hashed123','DHA','Karachi','customer'),
('44444444-4444-4444-4444-444444444444','Ayesha Noor','ayesha@example.com','03211234567','hashed123','Model Town','Lahore','customer'),
('55555555-5555-5555-5555-555555555555','Hamza Ali','hamza@example.com','03331234567','hashed123','Satellite Town','Rawalpindi','customer'),
('66666666-6666-6666-6666-666666666666','Fatima Khan','fatima@example.com','03451234567','hashed123','University Road','Peshawar','customer'),
('77777777-7777-7777-7777-777777777777','Admin User','admin@jamalcart.com','03551234567','adminhash','Head Office','Karachi','admin');

INSERT INTO products (name, description, category_id, subcategory, sku, slug, brand, price, stock, rating, image_url) VALUES
('Cotton T-Shirt','Comfortable cotton t-shirt',1,'T-Shirts','SKU001','cotton-tshirt','Jamal',999,50,4.5,'/images/products/tshirt.jpg'),
('Denim Jeans','Blue denim jeans',1,'Jeans','SKU002','denim-jeans','Levis',2499,40,4.6,'/images/products/jeans.jpg'),
('Floral Dress','Womens floral dress',2,'Dresses','SKU003','floral-dress','Ideas',2999,35,4.8,'/images/products/dress.jpg'),
('Kids School Bag','Waterproof school bag',3,'School Bags','SKU004','kids-school-bag','Jamal',1499,60,4.4,'/images/products/bag.jpg'),
('Wireless Earbuds','Bluetooth earbuds',4,'Audio','SKU005','wireless-earbuds','Redmi',2999,70,4.7,'/images/products/earbuds.jpg'),
('Running Shoes','Comfortable running shoes',5,'Shoes','SKU006','running-shoes','Nike',3999,30,4.9,'/images/products/shoes.jpg'),
('Leather Wallet','Premium leather wallet',6,'Wallet','SKU007','leather-wallet','Jamal',1199,45,4.3,'/images/products/wallet.jpg');

INSERT INTO cart (user_id, product_id, quantity) VALUES
('11111111-1111-1111-1111-111111111111',1,2),
('22222222-2222-2222-2222-222222222222',3,1),
('33333333-3333-3333-3333-333333333333',5,1),
('44444444-4444-4444-4444-444444444444',2,1),
('55555555-5555-5555-5555-555555555555',7,3),
('66666666-6666-6666-6666-666666666666',4,1),
('77777777-7777-7777-7777-777777777777',6,2);

INSERT INTO wishlist (user_id, product_id) VALUES
('11111111-1111-1111-1111-111111111111',5),
('22222222-2222-2222-2222-222222222222',6),
('33333333-3333-3333-3333-333333333333',2),
('44444444-4444-4444-4444-444444444444',1),
('55555555-5555-5555-5555-555555555555',3),
('66666666-6666-6666-6666-666666666666',7),
('77777777-7777-7777-7777-777777777777',4);

INSERT INTO orders (user_id, status, payment_method, shipping_address, total) VALUES
('11111111-1111-1111-1111-111111111111','Delivered','COD','Karachi',1998),
('22222222-2222-2222-2222-222222222222','Pending','JazzCash','Karachi',2999),
('33333333-3333-3333-3333-333333333333','Shipped','EasyPaisa','Karachi',2999),
('44444444-4444-4444-4444-444444444444','Processing','COD','Lahore',2499),
('55555555-5555-5555-5555-555555555555','Cancelled','Card','Rawalpindi',1199),
('66666666-6666-6666-6666-666666666666','Delivered','Bank Transfer','Peshawar',1499),
('77777777-7777-7777-7777-777777777777','Paid','COD','Karachi',3999);

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1,1,2,999),
(2,3,1,2999),
(3,5,1,2999),
(4,2,1,2499),
(5,7,1,1199),
(6,4,1,1499),
(7,6,1,3999);

INSERT INTO payments (order_id, method, status, transaction_id, paid_at) VALUES
(1,'COD','Paid','TXN001',NOW()),
(2,'JazzCash','Pending','TXN002',NOW()),
(3,'EasyPaisa','Paid','TXN003',NOW()),
(4,'COD','Pending','TXN004',NOW()),
(5,'Card','Refunded','TXN005',NOW()),
(6,'Bank Transfer','Paid','TXN006',NOW()),
(7,'COD','Paid','TXN007',NOW());

INSERT INTO reviews (product_id, user_id, rating, review) VALUES
(1,'11111111-1111-1111-1111-111111111111',5,'Excellent quality.'),
(2,'22222222-2222-2222-2222-222222222222',4,'Comfortable jeans.'),
(3,'33333333-3333-3333-3333-333333333333',5,'Beautiful dress.'),
(4,'44444444-4444-4444-4444-444444444444',4,'Good school bag.'),
(5,'55555555-5555-5555-5555-555555555555',5,'Excellent sound quality.'),
(6,'66666666-6666-6666-6666-666666666666',5,'Very comfortable shoes.'),
(7,'77777777-7777-7777-7777-777777777777',4,'Nice wallet.');

INSERT INTO coupons (code, discount, expiry_date) VALUES
('WELCOME10',10,'2027-12-31'),
('SUMMER20',20,'2027-08-31'),
('EID15',15,'2027-04-20'),
('SAVE100',100,'2027-10-15'),
('FREESHIP',250,'2027-12-31'),
('NEWUSER',12,'2027-09-30'),
('FLASH25',25,'2027-11-30');

INSERT INTO chatbot_logs (user_id, question, intent, response) VALUES
('11111111-1111-1111-1111-111111111111','Show electronics','show_products','Here are our electronics.'),
('22222222-2222-2222-2222-222222222222','Track my order','track_order','Your order is pending.'),
('33333333-3333-3333-3333-333333333333','Update my address','update_shipping_address','Please enter your new address.'),
('44444444-4444-4444-4444-444444444444','Cancel my order','cancel_order','Your order has been cancelled.'),
('55555555-5555-5555-5555-555555555555','Show shoes','search_product','Here are some shoes.'),
('66666666-6666-6666-6666-666666666666','Refund my order','refund_order','Refund request submitted.'),
('77777777-7777-7777-7777-777777777777','Show deals','deals','These are today''s deals.');