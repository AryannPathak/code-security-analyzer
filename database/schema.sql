-- ========================================================================
-- SMARTFLOW: AI-POWERED RETAIL & E-COMMERCE MANAGEMENT SYSTEM
-- MASTER DATABASE SCHEMA (MySQL 8.0+ / MariaDB)
-- 
-- System Architecture: Centralized Omnichannel Retail Architecture
-- Combines: DMart (Physical Stores/POS) + Amazon (Online Marketplace)
-- Author: AIML Engineering Project
-- ========================================================================

CREATE DATABASE IF NOT EXISTS smartflow_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE smartflow_db;

-- ------------------------------------------------------------------------
-- 1. USERS TABLE
-- Authentication and base credentials for all system participants.
-- Roles: ADMIN, CUSTOMER, EMPLOYEE
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(60) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'CUSTOMER', 'EMPLOYEE') NOT NULL DEFAULT 'CUSTOMER',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_role (role),
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 2. CUSTOMERS TABLE
-- Extended profile information for e-commerce and retail loyalty buyers.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NULL,
    address TEXT NULL,
    city VARCHAR(60) NULL,
    postal_code VARCHAR(20) NULL,
    total_orders INT NOT NULL DEFAULT 0,
    total_spent DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_customers_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_customer_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 3. STORES TABLE
-- Physical DMart retail branches and centralized fulfillment hubs.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    location VARCHAR(255) NOT NULL,
    city VARCHAR(60) NOT NULL,
    phone VARCHAR(20) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_store_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 4. EMPLOYEES TABLE
-- Store staff, POS cashiers, managers, and inventory clerks.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    store_id INT NULL,
    employee_code VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    position VARCHAR(60) NOT NULL DEFAULT 'Cashier',
    shift ENUM('MORNING', 'EVENING', 'NIGHT', 'GENERAL') NOT NULL DEFAULT 'GENERAL',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_employees_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_employees_store FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE SET NULL,
    INDEX idx_employee_store (store_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 5. CATEGORIES TABLE
-- Product hierarchy for both online catalog navigation and supermarket aisles.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    image_url VARCHAR(255) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 6. PRODUCTS TABLE
-- Centralized product catalog shared between DMart POS and Amazon storefront.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    barcode VARCHAR(60) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    brand VARCHAR(100) NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'piece',
    mrp DECIMAL(10, 2) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(255) NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_product_barcode (barcode),
    INDEX idx_product_name (name),
    INDEX idx_product_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 7. INVENTORY TABLE
-- Store-wise and warehouse-wise stock levels with safety thresholds.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    product_id INT NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    safety_stock_level INT NOT NULL DEFAULT 15,
    reorder_quantity INT NOT NULL DEFAULT 60,
    last_restocked_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_store_product UNIQUE (store_id, product_id),
    CONSTRAINT fk_inv_store FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    CONSTRAINT fk_inv_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_inv_low_stock (stock_quantity, safety_stock_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 8. ORDERS TABLE
-- Unified order ledger capturing both ONLINE (Amazon) and STORE (DMart POS).
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NULL,
    store_id INT NOT NULL,
    employee_id INT NULL,
    order_type ENUM('ONLINE', 'STORE') NOT NULL,
    order_status ENUM('PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'COMPLETED',
    subtotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    shipping_address TEXT NULL,
    idempotency_key VARCHAR(100) NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    CONSTRAINT fk_orders_store FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL,
    INDEX idx_orders_status (order_status),
    INDEX idx_orders_type (order_type),
    INDEX idx_orders_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 9. ORDER_ITEMS TABLE
-- Line items for each order with historical snapshot of unit prices.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    INDEX idx_order_items_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 10. TRANSACTIONS TABLE
-- Financial transaction ledger. Evaluated by AIML Isolation Forest.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(60) NOT NULL UNIQUE,
    order_id INT NOT NULL,
    customer_id INT NULL,
    store_id INT NOT NULL,
    source ENUM('ONLINE', 'STORE') NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    status ENUM('SUCCESS', 'FAILED', 'REFUNDED', 'PENDING') NOT NULL DEFAULT 'SUCCESS',
    payment_method ENUM('CASH', 'UPI', 'CARD', 'ONLINE_NETBANKING') NOT NULL,
    is_flagged_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
    anomaly_score FLOAT NOT NULL DEFAULT 0.0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_txn_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE RESTRICT,
    CONSTRAINT fk_txn_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    CONSTRAINT fk_txn_store FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE RESTRICT,
    INDEX idx_txn_status (status),
    INDEX idx_txn_flagged (is_flagged_anomaly),
    INDEX idx_txn_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 11. PAYMENT_RECORDS TABLE
-- Auditable log of simulated gateway authorizations and tender responses.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payment_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    payment_gateway_ref VARCHAR(100) NULL,
    payment_method ENUM('CASH', 'UPI', 'CARD', 'ONLINE_NETBANKING') NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    status ENUM('SUCCESS', 'FAILED', 'REFUNDED') NOT NULL,
    response_message TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pay_txn FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    INDEX idx_pay_gateway_ref (payment_gateway_ref)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 12. CART TABLE
-- Active shopping cart sessions for online customers.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_cart_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 13. CART_ITEMS TABLE
-- Items present inside a customer's active online cart.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_cart_product UNIQUE (cart_id, product_id),
    CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id) REFERENCES cart(id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 14. COUPONS TABLE
-- Promotional discount codes and checkout validation rules.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coupons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    discount_percent DECIMAL(5, 2) NOT NULL,
    max_discount_amount DECIMAL(10, 2) NULL,
    min_order_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    usage_limit INT NOT NULL DEFAULT 1000,
    used_count INT NOT NULL DEFAULT 0,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_coupon_code (code, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 15. STOCK_HISTORY TABLE
-- Immutable inventory audit trail tracking every stock in/out event.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    change_type ENUM('RESTOCK', 'ONLINE_SALE', 'STORE_SALE', 'RETURN', 'DAMAGE_ADJUSTMENT') NOT NULL,
    quantity_changed INT NOT NULL,
    balance_after INT NOT NULL,
    reference_id VARCHAR(60) NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hist_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    CONSTRAINT fk_hist_store FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE RESTRICT,
    INDEX idx_hist_prod_store (product_id, store_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 16. RETURNS TABLE
-- Product return requests and simulated refund records.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS returns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    refund_amount DECIMAL(10, 2) NOT NULL,
    reason TEXT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'COMPLETED') NOT NULL DEFAULT 'PENDING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_returns_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_returns_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 17. RECOMMENDATIONS TABLE
-- Precomputed AIML popularity & collaborative recommendation scores.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    score DECIMAL(6, 4) NOT NULL DEFAULT 0.0000,
    strategy VARCHAR(50) NOT NULL DEFAULT 'POPULARITY',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_rec_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_rec_strategy (strategy, score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------
-- 18. AUDIT_LOGS TABLE
-- Security & enterprise compliance logging for all sensitive mutations.
-- ------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NULL,
    entity_id VARCHAR(50) NULL,
    ip_address VARCHAR(45) NULL,
    details TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_action (action),
    INDEX idx_audit_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================================================
-- INITIAL SEED: DEFAULT CENTRAL HUB STORE & SUPERADMIN SEED PLACEHOLDER
-- (Passwords are managed via Werkzeug security in the Python backend)
-- ========================================================================
INSERT INTO stores (id, store_code, name, location, city, phone, is_active)
VALUES 
    (1, 'HUB-001', 'SmartFlow Central Warehouse & E-Commerce Hub', 'Sector 18, Industrial Area', 'Mumbai', '+91 98765 00001', TRUE),
    (2, 'DMRT-101', 'SmartFlow DMart Retail Store - Andheri West', 'SV Road, Andheri West', 'Mumbai', '+91 98765 00002', TRUE),
    (3, 'DMRT-102', 'SmartFlow DMart Retail Store - Whitefield', 'ITPL Main Road, Whitefield', 'Bengaluru', '+91 98765 00003', TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO categories (id, name, description, image_url, is_active)
VALUES
    (1, 'Groceries & Staples', 'Rice, Dal, Atta, Cooking Oils, Spices, Grains', 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80', TRUE),
    (2, 'Electronics & Gadgets', 'Smartphones, Audio, Cables, Laptops, Accessories', 'https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&w=400&q=80', TRUE),
    (3, 'Clothing & Fashion', 'Men, Women, Kids Apparel and Footwear', 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=400&q=80', TRUE),
    (4, 'Home Appliances', 'Kitchen appliances, Coolers, Vacuums, Irons', 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=400&q=80', TRUE),
    (5, 'Personal Care', 'Skin care, Shampoos, Oral care, Perfumes', 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=400&q=80', TRUE),
    (6, 'Food & Beverages', 'Packaged snacks, Biscuits, Tea, Coffee, Juices', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80', TRUE),
    (7, 'Household Essentials', 'Cleaners, Detergents, Mops, Kitchenware', 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=400&q=80', TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO coupons (id, code, discount_percent, max_discount_amount, min_order_amount, usage_limit, used_count, expires_at, is_active)
VALUES
    (1, 'WELCOME50', 10.00, 200.00, 500.00, 10000, 0, '2028-12-31 23:59:59', TRUE),
    (2, 'FESTIVE20', 20.00, 500.00, 1200.00, 5000, 0, '2028-12-31 23:59:59', TRUE),
    (3, 'SUPERMART5', 5.00, 100.00, 300.00, 50000, 0, '2028-12-31 23:59:59', TRUE)
ON DUPLICATE KEY UPDATE code=VALUES(code);
