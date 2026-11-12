# SmartFlow REST API Documentation

**Application:** SmartFlow – AI-Powered Retail & E-Commerce Management System  
**Version:** 1.0.0  
**Base URL:** `http://localhost:5000/api`  
**Authentication Scheme:** JSON Web Tokens (JWT) Bearer Token in `Authorization: Bearer <TOKEN>` header.

---

## Table of Contents
1. [Authentication Endpoints (`/api/auth`)](#1-authentication-endpoints)
2. [Product & Catalog Endpoints (`/api/products`)](#2-product--catalog-endpoints)
3. [Store & POS Endpoints (`/api/pos`, `/api/stores`)](#3-store--pos-endpoints)
4. [Order & Checkout Endpoints (`/api/orders`)](#4-order--checkout-endpoints)
5. [Shopping Cart Endpoints (`/api/cart`)](#5-shopping-cart-endpoints)
6. [Coupon Management (`/api/coupons`)](#6-coupon-management)
7. [Centralized Transactions & Audit (`/api/transactions`)](#7-centralized-transactions)
8. [AIML Predictive Endpoints (`/api/ai`)](#8-aiml-predictive-endpoints)
9. [Analytics & KPI Dashboard (`/api/analytics`)](#9-analytics--kpi-dashboard)

---

## 1. Authentication Endpoints

### 1.1 Customer Registration
- **Endpoint:** `POST /api/auth/register`
- **Access:** Public
- **Request Body:**
```json
{
  "username": "aarav_mehta",
  "email": "aarav@example.com",
  "password": "SecurePassword@123",
  "full_name": "Aarav Mehta",
  "phone": "9876543210",
  "address": "Flat 402, Sunshine Heights",
  "city": "Mumbai"
}
```
- **Response (201 Created):**
```json
{
  "success": true,
  "message": "Registration successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 105,
    "username": "aarav_mehta",
    "email": "aarav@example.com",
    "role": "CUSTOMER"
  }
}
```

### 1.2 User Login
- **Endpoint:** `POST /api/auth/login`
- **Access:** Public
- **Request Body:**
```json
{
  "username": "admin",
  "password": "Admin@12345"
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "message": "Welcome back, admin!",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@smartflow.local",
    "role": "ADMIN"
  }
}
```

### 1.3 User Profile
- **Endpoint:** `GET /api/auth/profile`
- **Access:** Authenticated (Bearer JWT)
- **Response (200 OK):** Returns complete user profile including customer or employee role metadata.

---

## 2. Product & Catalog Endpoints

### 2.1 List Products (Search & Filter)
- **Endpoint:** `GET /api/products`
- **Access:** Public
- **Query Parameters:**
  - `search` (string): Keyword matching name, brand, SKU, or barcode.
  - `category_id` (integer): Filter by product category.
  - `min_price`, `max_price` (float): Filter price boundary.
  - `sort_by` (string): `price_asc`, `price_desc`, `name_asc`, `newest`.
  - `page` (integer, default 1), `per_page` (integer, default 20).
- **Response (200 OK):**
```json
{
  "success": true,
  "total": 1000,
  "pages": 50,
  "current_page": 1,
  "products": [
    {
      "id": 1,
      "sku": "GRO-9482-A7",
      "barcode": "890123400001",
      "name": "Daawat Rozana Super Basmati Rice 5kg",
      "brand": "Daawat",
      "unit": "kg",
      "mrp": 550.0,
      "price": 449.0,
      "category_name": "Groceries",
      "total_stock": 100,
      "is_available": true
    }
  ]
}
```

### 2.2 Barcode & SKU Lookup (POS Fast Scan)
- **Endpoint:** `GET /api/products/barcode/<barcode_or_sku>`
- **Access:** Public / POS Terminal
- **Response (200 OK):** Instant return of product details with store-by-store inventory stock.

### 2.3 Create Product
- **Endpoint:** `POST /api/products`
- **Access:** Admin only
- **Request Body:**
```json
{
  "category_id": 1,
  "name": "Tata Tea Gold 500g",
  "brand": "Tata",
  "unit": "pack",
  "cost_price": 180.0,
  "price": 240.0,
  "mrp": 275.0,
  "initial_stock": 50
}
```

---

## 3. Store & POS Endpoints

### 3.1 DMart POS Fast Checkout
- **Endpoint:** `POST /api/pos/checkout`
- **Access:** Employee / Cashier
- **Request Body:**
```json
{
  "store_id": 2,
  "payment_method": "CASH",
  "customer_phone": "9876543210",
  "customer_name": "Walk-in Customer",
  "coupon_code": "SAVE10",
  "idempotency_key": "POS-MALAD-2026-94821",
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 14, "quantity": 1 }
  ]
}
```
- **Response (201 Created):**
```json
{
  "success": true,
  "message": "Bill generated and stock deducted successfully.",
  "data": {
    "order": {
      "id": 10001,
      "order_number": "ORD-STR2-20261112-010001",
      "order_type": "STORE",
      "order_status": "COMPLETED",
      "total_amount": 1024.15
    },
    "receipt": {
      "bill_number": "ORD-STR2-20261112-010001",
      "store_name": "DMart Andheri West",
      "store_location": "Link Road, Andheri West, Mumbai",
      "date": "12-Nov-2026 07:15 PM",
      "items_count": 2,
      "subtotal": 1020.0,
      "discount": 50.0,
      "tax_5pct": 48.5,
      "final_total": 1018.5,
      "payment_method": "CASH",
      "payment_ref": "SIM-PAY-98A7B6C5"
    }
  }
}
```

---

## 4. Order & Checkout Endpoints

### 4.1 Place Online Order (Amazon E-Commerce)
- **Endpoint:** `POST /api/orders`
- **Access:** Customer
- **Request Body:**
```json
{
  "store_id": 1,
  "payment_method": "UPI",
  "coupon_code": "SAVE10",
  "shipping_address": "Flat 402, Sunshine Heights, Mumbai",
  "idempotency_key": "CHECKOUT-UUID-9182",
  "items": [
    { "product_id": 5, "quantity": 1 }
  ]
}
```

### 4.2 Cancel Order
- **Endpoint:** `PUT /api/orders/<order_id>/cancel`
- **Access:** Customer (own orders) or Admin
- **Behavior:** Updates order status to `CANCELLED`, issues full refund record, and executes automated stock return restoration into inventory.

---

## 5. Centralized Transactions & Export

### 5.1 Query Centralized Ledger
- **Endpoint:** `GET /api/transactions`
- **Access:** Admin only
- **Query Parameters:** `source` (ONLINE/STORE), `status`, `payment_method`, `start_date`, `end_date`, `page`.

### 5.2 Export Transaction CSV
- **Endpoint:** `GET /api/transactions/export`
- **Access:** Admin only
- **Response:** Streaming CSV file `smartflow_transactions_<timestamp>.csv` containing all centralized transaction columns.

---

## 6. AIML Predictive Endpoints

### 6.1 Sales Prediction (Linear Regression)
- **Endpoint:** `GET /api/ai/predict-sales?days_ahead=7`
- **Access:** Employee / Admin
- **Response (200 OK):**
```json
{
  "success": true,
  "algorithm": "Linear Regression (Ordinary Least Squares)",
  "metrics": {
    "mae": 1279.17,
    "rmse": 1506.71,
    "r2_score": 0.8519,
    "train_samples": 72,
    "test_samples": 18
  },
  "future_forecast": [
    { "date": "2026-11-13", "predicted_sales": 32800.0 },
    { "date": "2026-11-14", "predicted_sales": 36100.0 }
  ]
}
```

### 6.2 Product Recommendations (Popularity Frequency)
- **Endpoint:** `GET /api/ai/recommendations?limit=8`
- **Access:** Public

### 6.3 Unusual Transaction Anomaly Detection (Isolation Forest)
- **Endpoint:** `GET /api/ai/anomalies`
- **Access:** Admin only
- **Response (200 OK):** Returns top anomalous transactions with mathematical anomaly scores and explanation tags.

### 6.4 Inventory Demand Forecasting (Moving Average)
- **Endpoint:** `GET /api/ai/inventory-forecast?store_id=2`
- **Access:** Employee / Admin
- **Response (200 OK):** Returns product-by-product daily demand velocity, days remaining before stockout, and priority restock alerts (`CRITICAL`, `HIGH`, `NORMAL`).
