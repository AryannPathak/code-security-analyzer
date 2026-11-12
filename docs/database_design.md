# SMARTFLOW DATABASE DESIGN SPECIFICATION
## Comprehensive Data Dictionary & Schema Architecture

---

### 1. Database Overview & Design Principles

The SMARTFLOW database is built around **three foundational enterprise engineering principles**:

1. **Unified Catalog & Centralized Inventory**: Online storefront buyers and offline DMart store cashiers view the exact same SKU numbers, barcodes, and master prices. Inventory is partitioned by physical store (`store_id`) and warehouse hubs, with real-time decrements upon verified checkout.
2. **Unified Financial Ledger (`transactions`)**: Whether an order originates from an online e-commerce cart (`order_type = 'ONLINE'`) or a brick-and-mortar DMart POS terminal (`order_type = 'STORE'`), the resulting financial transaction is committed to the central `transactions` table. This provides a single source of truth for business intelligence, cashier reconciliation, and the AIML Anomaly Detection model.
3. **Transactional Integrity & Concurrency Safeguards**:
   - Stock updates utilize database transactions with row-level locks (`with_for_update()`) to prevent race conditions when multiple customers or cashiers checkout the final item simultaneously.
   - Orders support unique `idempotency_key` values to eliminate double-billing caused by accidental duplicate HTTP requests or browser refreshes.

---

### 2. Comprehensive Data Dictionary (18 Tables)

#### Table 1: `users`
Central identity repository for all system participants.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Unique user identifier |
| `username` | VARCHAR(60) | UNIQUE, NOT NULL, INDEX | Login username |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL, INDEX | Primary email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Werkzeug/Argon2/bcrypt secure password hash |
| `role` | VARCHAR(20) | NOT NULL, INDEX | Access tier: `'ADMIN'`, `'CUSTOMER'`, `'EMPLOYEE'` |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account state |
| `last_login` | DATETIME | NULLABLE | Timestamp of most recent authentication |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Last record modification timestamp |

---

#### Table 2: `customers`
Profile details for online customers and retail loyalty members.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Customer identity |
| `user_id` | INT | UNIQUE, FK -> `users.id` (CASCADE) | Associated authentication user |
| `full_name` | VARCHAR(100) | NOT NULL | Customer full legal name |
| `phone` | VARCHAR(20) | NULLABLE, INDEX | Contact phone number |
| `address` | TEXT | NULLABLE | Default shipping street address |
| `city` | VARCHAR(60) | NULLABLE | City of residence |
| `postal_code` | VARCHAR(20) | NULLABLE | Postal/ZIP code |
| `total_orders` | INT | NOT NULL, DEFAULT 0 | Aggregated lifetime order count |
| `total_spent` | DECIMAL(12, 2) | NOT NULL, DEFAULT 0.00 | Aggregated lifetime expenditure (₹) |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Profile creation timestamp |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Last profile update |

---

#### Table 3: `stores`
Physical DMart retail store locations and e-commerce distribution warehouses.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Store branch identifier |
| `store_code` | VARCHAR(20) | UNIQUE, NOT NULL, INDEX | Branch code (e.g., `'DMRT-101'`, `'HUB-001'`) |
| `name` | VARCHAR(120) | NOT NULL | Store display name |
| `location` | VARCHAR(255) | NOT NULL | Street address and landmark |
| `city` | VARCHAR(60) | NOT NULL, INDEX | City location |
| `phone` | VARCHAR(20) | NULLABLE | Store contact telephone |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Operating status |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Branch onboarding date |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Last modification |

---

#### Table 4: `employees`
Store cashiers, inventory clerks, and shift supervisors.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Employee identity |
| `user_id` | INT | UNIQUE, FK -> `users.id` (CASCADE) | Associated login user |
| `store_id` | INT | NULLABLE, FK -> `stores.id` (SET NULL) | Assigned primary store branch |
| `employee_code` | VARCHAR(30) | UNIQUE, NOT NULL | Human-readable staff badge code |
| `full_name` | VARCHAR(100) | NOT NULL | Full name of staff member |
| `position` | VARCHAR(60) | NOT NULL, DEFAULT 'Cashier' | Job title: Cashier, Store Manager, Clerk |
| `shift` | VARCHAR(20) | NOT NULL, DEFAULT 'GENERAL' | Working shift: MORNING, EVENING, NIGHT |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Employment status |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date of hiring |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Last record update |

---

#### Table 5: `categories`
Hierarchical product classification aisles.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Category ID |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Category name (e.g., 'Groceries & Staples') |
| `description` | TEXT | NULLABLE | Detailed description of items in category |
| `image_url` | VARCHAR(255) | NULLABLE | Category visual badge thumbnail |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Visibility flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Last update |

---

#### Table 6: `products`
Central master product catalog.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Product ID |
| `category_id` | INT | NOT NULL, FK -> `categories.id` (RESTRICT) | Parent category |
| `sku` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Stock Keeping Unit identifier |
| `barcode` | VARCHAR(60) | UNIQUE, NOT NULL, INDEX | Standard EAN-13/UPC barcode for POS scanning |
| `name` | VARCHAR(200) | NOT NULL, INDEX | Product name |
| `description` | TEXT | NULLABLE | Detailed product specs and composition |
| `brand` | VARCHAR(100) | NULLABLE | Manufacturer/Brand name |
| `unit` | VARCHAR(20) | NOT NULL, DEFAULT 'piece' | Unit of measurement (piece, kg, litre, pack) |
| `mrp` | DECIMAL(10, 2) | NOT NULL | Maximum Retail Price printed on packaging |
| `price` | DECIMAL(10, 2) | NOT NULL | Effective selling price |
| `cost_price` | DECIMAL(10, 2) | NOT NULL | Procurement cost price |
| `image_url` | VARCHAR(255) | NULLABLE | Product high-res photo URL |
| `is_available` | BOOLEAN | NOT NULL, DEFAULT TRUE | Availability for ordering |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Catalog entry timestamp |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Last modified timestamp |

---

#### Table 7: `inventory`
Store-wise stock tracking with safety thresholds.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Inventory record ID |
| `store_id` | INT | NOT NULL, FK -> `stores.id` (CASCADE) | Physical store / warehouse |
| `product_id` | INT | NOT NULL, FK -> `products.id` (CASCADE) | Tracked item |
| `stock_quantity` | INT | NOT NULL, DEFAULT 0 | Current physically available units |
| `safety_stock_level` | INT | NOT NULL, DEFAULT 15 | Threshold triggering low-stock alert |
| `reorder_quantity` | INT | NOT NULL, DEFAULT 60 | Recommended batch order quantity |
| `last_restocked_at` | DATETIME | NULLABLE | Timestamp of latest stock shipment arrival |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record initialized date |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Last quantity modification |

*Unique Constraint*: `UNIQUE(store_id, product_id)` ensures no duplicate inventory records per store.

---

#### Table 8: `orders`
Master order record header.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Internal order ID |
| `order_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Public reference (e.g. `'ORD-202611-9214'`) |
| `customer_id` | INT | NULLABLE, FK -> `customers.id` (SET NULL) | Registered buyer (or NULL for walk-in POS) |
| `store_id` | INT | NOT NULL, FK -> `stores.id` (RESTRICT) | Store fulfilling or billing the order |
| `employee_id` | INT | NULLABLE, FK -> `employees.id` (SET NULL) | Cashier who scanned bill (NULL for online) |
| `order_type` | VARCHAR(20) | NOT NULL, INDEX | Origin: `'ONLINE'` or `'STORE'` |
| `order_status` | VARCHAR(30) | NOT NULL, DEFAULT 'COMPLETED', INDEX | Order state machine flag |
| `subtotal` | DECIMAL(12, 2) | NOT NULL, DEFAULT 0.00 | Pre-discount, pre-tax merchandise sum |
| `discount_amount` | DECIMAL(12, 2) | NOT NULL, DEFAULT 0.00 | Coupon or promo discount deducted |
| `tax_amount` | DECIMAL(12, 2) | NOT NULL, DEFAULT 0.00 | GST/Sales tax applied |
| `total_amount` | DECIMAL(12, 2) | NOT NULL, DEFAULT 0.00 | Final payable invoice total |
| `shipping_address` | TEXT | NULLABLE | Delivery destination for online orders |
| `idempotency_key` | VARCHAR(100) | UNIQUE, NULLABLE | Client idempotency token to avoid double charges |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP, INDEX | Order placement timestamp |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Status modification timestamp |

---

#### Table 9: `order_items`
Line items attached to an order.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Line item ID |
| `order_id` | INT | NOT NULL, FK -> `orders.id` (CASCADE) | Parent order |
| `product_id` | INT | NOT NULL, FK -> `products.id` (RESTRICT) | Purchased item |
| `quantity` | INT | NOT NULL | Number of units purchased |
| `unit_price` | DECIMAL(10, 2) | NOT NULL | Price snapshot at time of checkout |
| `subtotal` | DECIMAL(12, 2) | NOT NULL | Calculated (`quantity * unit_price`) |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp |

---

#### Table 10: `transactions`
Unified financial transaction ledger.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Internal transaction ID |
| `transaction_id` | VARCHAR(60) | UNIQUE, NOT NULL, INDEX | Transaction reference (e.g. `'TXN-8849-0012'`) |
| `order_id` | INT | NOT NULL, FK -> `orders.id` (RESTRICT) | Target order |
| `customer_id` | INT | NULLABLE, FK -> `customers.id` (SET NULL) | Buyer ID |
| `store_id` | INT | NOT NULL, FK -> `stores.id` (RESTRICT) | Originating branch |
| `source` | VARCHAR(20) | NOT NULL | Origin channel: `'ONLINE'` or `'STORE'` |
| `amount` | DECIMAL(12, 2) | NOT NULL | Total financial value settled |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'SUCCESS', INDEX | State: `'SUCCESS'`, `'FAILED'`, `'REFUNDED'` |
| `payment_method` | VARCHAR(30) | NOT NULL | Tender: `'CASH'`, `'UPI'`, `'CARD'`, `'ONLINE_NETBANKING'` |
| `is_flagged_anomaly`| BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | AIML Isolation Forest anomaly indicator |
| `anomaly_score` | FLOAT | NOT NULL, DEFAULT 0.0 | Numerical outlier score (-1.0 to 1.0) |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP, INDEX | Timestamp of financial settlement |
| `updated_at` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | Modification timestamp |

---

#### Table 11: `payment_records`
Simulated payment gateway authorization log.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Payment record ID |
| `transaction_id` | INT | NOT NULL, FK -> `transactions.id` (CASCADE) | Linked financial transaction |
| `payment_gateway_ref` | VARCHAR(100)| NULLABLE, INDEX | Simulated Razorpay/Stripe authorization token |
| `payment_method` | VARCHAR(30) | NOT NULL | Payment instrument |
| `amount` | DECIMAL(12, 2) | NOT NULL | Settlement currency amount |
| `status` | VARCHAR(20) | NOT NULL | Gateway response status |
| `response_message` | TEXT | NULLABLE | Simulated bank response message |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Execution timestamp |

---

#### Table 12: `cart` & Table 13: `cart_items`
Persistent shopping cart session for customer web accounts.

- `cart`: `id` (PK), `customer_id` (Unique FK to `customers.id`), `created_at`, `updated_at`
- `cart_items`: `id` (PK), `cart_id` (FK to `cart.id`), `product_id` (FK to `products.id`), `quantity`, `created_at`, `updated_at`. Unique constraint `(cart_id, product_id)`.

---

#### Table 14: `coupons`
Promotional codes and discount rules.

- `id` (PK), `code` (Unique), `discount_percent`, `max_discount_amount`, `min_order_amount`, `usage_limit`, `used_count`, `expires_at`, `is_active`, `created_at`, `updated_at`.

---

#### Table 15: `stock_history`
Full audit trail of stock adjustments.

- `id` (PK), `product_id` (FK), `store_id` (FK), `change_type` (`RESTOCK`, `ONLINE_SALE`, `STORE_SALE`, `RETURN`, `DAMAGE_ADJUSTMENT`), `quantity_changed` (positive or negative integer), `balance_after`, `reference_id` (Order number or invoice code), `notes`, `created_at`.

---

#### Table 16: `returns`
Product return tickets and refund status tracking.

- `id` (PK), `order_id` (FK), `product_id` (FK), `quantity`, `refund_amount`, `reason`, `status` (`PENDING`, `APPROVED`, `REJECTED`, `COMPLETED`), `created_at`, `updated_at`.

---

#### Table 17: `recommendations`
Pre-calculated AIML collaborative filtering and popularity scores.

- `id` (PK), `product_id` (FK), `score`, `strategy` (`POPULARITY`, `CATEGORY_TREND`), `is_active`, `updated_at`.

---

#### Table 18: `audit_logs`
Enterprise security logging for critical actions (logins, stock corrections, anomaly inspections).

- `id` (PK), `user_id` (FK), `action`, `entity_type`, `entity_id`, `ip_address`, `details`, `created_at`.

---

### 3. Database Indexes Rationale

| Index | Target Table | Justification |
|---|---|---|
| `idx_product_barcode` | `products` | Essential for DMart POS barcode guns scanning 50+ items/minute |
| `idx_product_name` | `products` | Accelerates Amazon-style search queries across product titles |
| `idx_inv_low_stock` | `inventory` | Powers the admin dashboard instant low-stock alert query |
| `idx_orders_status` | `orders` | Enables fast filtering for pending vs completed orders |
| `idx_orders_type` | `orders` | Enables immediate online vs offline sales metric segregation |
| `idx_txn_flagged` | `transactions` | Allows the AI anomaly dashboard to instantly retrieve flagged records |
| `idx_txn_created` | `transactions` | Critical for fast date-range aggregations in sales analytics |
