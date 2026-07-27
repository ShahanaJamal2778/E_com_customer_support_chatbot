-- database/schema.sql
--
-- Reference copy of the schema already live in Supabase. This file is
-- NOT meant to be re-run against your current database - it exists so
-- the schema is version-controlled and reproducible (e.g. for a fresh
-- Supabase project, or for your FYP documentation/appendix).
--
-- NOTE: table creation order was corrected vs. the original script -
-- `categories` must exist before `products` since products.category_id
-- has a foreign key to it. Running the original order top-to-bottom in
-- a single transaction would fail with "relation categories does not
-- exist".

CREATE TABLE categories (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  image TEXT
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20) UNIQUE,
  password_hash TEXT NOT NULL,
  address TEXT,
  city VARCHAR(100),
  role VARCHAR(20) DEFAULT 'customer',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE products (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT,
  description TEXT,
  category_id BIGINT REFERENCES categories(id),
  subcategory TEXT,
  sku TEXT UNIQUE,
  slug TEXT UNIQUE,
  brand VARCHAR(50),
  price NUMERIC(10,2),
  stock INT DEFAULT 0,
  rating NUMERIC(2,1),
  image_url TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE cart (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  product_id BIGINT REFERENCES products(id),
  quantity INTEGER DEFAULT 1,
  UNIQUE(user_id, product_id)
);

CREATE TABLE wishlist (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  product_id BIGINT REFERENCES products(id),
  UNIQUE(user_id, product_id)
);

CREATE TABLE orders (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  status VARCHAR(20) CHECK (
    status IN ('Pending','Paid','Processing','Shipped','Delivered','Cancelled','Refunded')
  ),
  payment_method VARCHAR(20) CHECK (
    payment_method IN ('COD','JazzCash','EasyPaisa','Bank Transfer','Card')
  ),
  shipping_address TEXT,
  total NUMERIC,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE order_items (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id BIGINT REFERENCES orders(id),
  product_id BIGINT REFERENCES products(id),
  quantity INT CHECK (quantity > 0),
  price INT CHECK (price >= 0)
);

CREATE TABLE payments (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id BIGINT REFERENCES orders(id),
  method TEXT,
  status TEXT,
  transaction_id TEXT,
  paid_at TIMESTAMP
);

CREATE TABLE reviews (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_id BIGINT REFERENCES products(id),
  user_id UUID REFERENCES users(id),
  rating INT CHECK (rating BETWEEN 1 AND 5),
  review TEXT,
  UNIQUE(product_id, user_id)
);

CREATE TABLE coupons (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  code TEXT UNIQUE,
  discount INT CHECK (discount > 0),
  expiry_date DATE
);

CREATE TABLE chatbot_logs (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  question TEXT,
  intent TEXT,
  response TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_cart_user ON cart(user_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_logs_intent ON chatbot_logs(intent);