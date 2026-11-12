# SMARTFLOW: AI-POWERED RETAIL & E-COMMERCE MANAGEMENT SYSTEM

> **3rd-Year AIML Engineering Major Project**  
> *An Omnichannel Retail Platform Unifying DMart Brick-and-Mortar Retail POS + Amazon Digital E-Commerce Storefront + Predictive Machine Learning*

[![Status](https://img.shields.io/badge/Status-Complete%20%26%20Verified-emerald?style=for-the-badge)]()
[![Tests](https://img.shields.io/badge/Tests-35%2F35%20Passing-brightgreen?style=for-the-badge)]()
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite%205-blue?style=for-the-badge)]()
[![Backend](https://img.shields.io/badge/Backend-Python%20Flask%20%2B%20SQLAlchemy-yellow?style=for-the-badge)]()
[![AIML](https://img.shields.io/badge/AIML-Linear%20Regression%20%7C%20Isolation%20Forest-purple?style=for-the-badge)]()

---

## 📌 1. Project Overview

**SMARTFLOW** solves the fundamental fragmentation in the retail industry where physical supermarket operations (like **DMart**) and online digital storefronts (like **Amazon**) operate on disjointed software stacks. 

SmartFlow unites both worlds into a **single centralized database, inventory engine, and financial transaction ledger**, enhanced by 4 practical, beginner-to-intermediate machine learning algorithms:

1. **DMart-Style Physical Retail POS:** High-speed cashier billing terminal, barcode/SKU scanning, 5% GST tax and subtotal computation, instant thermal receipt modal, and atomic stock deductions.
2. **Amazon-Style Digital E-Commerce:** Product catalog browsing, multi-category filters, search, shopping cart with stepper, promotional coupon validation, simulated payment gateway (UPI, Card, Netbanking), and order tracking.
3. **Centralized Financial Ledger:** Both in-store counter bills (`STORE`) and digital orders (`ONLINE`) are captured in the same ledger with row-level database locking and idempotency protection against double billing.
4. **4 Practical AIML Models:**
   - **Sales Prediction:** Ordinary Least Squares (OLS) Linear Regression forecasting future daily revenue ($R^2 \approx 0.85$).
   - **Product Recommendations:** Popularity-based collaborative frequency ranking.
   - **Unusual Transaction Detection:** Unsupervised Isolation Forest (iForest) flagging statistical transaction outliers for admin audit review.
   - **Inventory Demand Forecasting:** Blended 7-Day & 30-Day Moving Average estimating stockout runway days and triggering restock alerts.

---

## 🚀 2. Quick Start: Running the Complete Application

### Prerequisites
- Python 3.11+ / Python 3.12 / Python 3.15
- Node.js 18+ and npm
- (Optional) MySQL 8.0 server (System automatically falls back to pre-seeded SQLite `smartflow.db` if MySQL is offline).

### Step 1: Start the Backend Server
Open a terminal in the project root:
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the Flask backend (starts on http://127.0.0.1:5000)
python backend/run.py
```

### Step 2: Start the Frontend Application
Open a second terminal:
```powershell
cd frontend
npm run dev
```
Open your browser at: **`http://localhost:5173`**

*(Note: The production bundle is also pre-built in `frontend/dist/` via `npm run build`.)*

---

## 🔑 3. Demo User Accounts (Pre-Seeded & Ready)

The application includes a **1-click Role Switcher Bar** in the top navigation header for examiners and evaluators to instantly switch roles without re-typing passwords:

| Role | Username | Password | Purpose & Permissions |
|---|---|---|---|
| **ADMIN** | `admin` | `Admin@12345` | Master dashboard, sales analytics, catalog CRUD, store inventory, audit logs, AIML insights. |
| **STORE EMPLOYEE** | `cashier_mumbai` | `Cashier@12345` | DMart POS cashier billing terminal, barcode gun scan, receipt printer. |
| **CUSTOMER** | `customer_demo` | `Customer@12345` | Amazon-style shopping storefront, cart, coupon `SAVE10`, checkout, order tracking. |

*(Additional pre-seeded customer accounts: `aarav_sharma_1`, `priya_patel_2`, `rohit_verma_3`, etc.)*

---

## 🧪 4. Running the Automated Test Suite

SmartFlow includes a comprehensive automated test suite with **35 unit, integration, concurrency, and AIML test cases**:

```powershell
# Run all 35 tests with Pytest
.\venv\Scripts\pytest tests/ -v
```

### Test Results Breakdown:
- `tests/test_phase1_setup.py`: Database connection, 18 model bindings (**3 passed**)
- `tests/test_auth.py`: JWT issuance, customer registration, password hashing (**6 passed**)
- `tests/test_products.py`: Catalog search, barcode scan, admin CRUD (**8 passed**)
- `tests/test_pos.py`: DMart POS fast billing, stock decrement, receipt format (**5 passed**)
- `tests/test_orders.py`: E-commerce checkout, idempotency key deduplication, cancellation & stock restoration (**5 passed**)
- `tests/test_aiml.py`: 4 AIML algorithms, MAE/RMSE/R² metrics, and predictive REST endpoints (**8 passed**)

**Result: 35 Passed, 0 Failed (100% Success Rate).**

---

## 📊 5. Master Dataset Summary

The system is populated with realistic retail data generated by `database/sample_data_generator.py`:

- **Categories:** 7 realistic retail departments (Groceries, Electronics, Personal Care, Household, Beverages, Snacks, Dairy).
- **Master Catalog:** **1,000 distinct retail products** with SKUs, standard barcodes (`890...`), MRP, and selling prices.
- **Physical Stores:** 3 DMart stores (Mumbai Flagship, Bangalore Central, Delhi NCR Hub).
- **Customers:** **500 registered customers** with addresses, phone numbers, and loyalty points.
- **Transactions & Orders:** **10,000 historical orders and transactions** spanning physical store purchases and online deliveries, providing authentic temporal patterns for AIML model training.

---

## 🤖 6. AIML Architecture & Implementation

### Feature 1: Sales Prediction (Linear Regression)
- **Algorithm:** Ordinary Least Squares (OLS) Linear Regression.
- **Features Extracted:** Secular trend index ($t$), day of week, day of month, weekend surge flag.
- **Evaluation:** Mean Absolute Error (MAE = ₹1,279.17), Root Mean Squared Error (RMSE = ₹1,506.71), Coefficient of Determination ($R^2 = 0.8519$).
- **Output:** 7-day future daily sales forecasts visualized via interactive Chart.js on the Admin Dashboard.

### Feature 2: Product Recommendations (Popularity Frequency)
- **Algorithm:** Collaborative frequency ranking.
- **Mechanism:** Analyzes historical `order_items` co-purchases to rank top-selling products.
- **Advantage:** Overcomes the cold-start problem for new shoppers while recommending high-turnover staples.

### Feature 3: Unusual Transaction Detection (Isolation Forest)
- **Algorithm:** Unsupervised Isolation Forest (iForest) tree ensemble.
- **Mechanism:** Recursively partitions multidimensional transaction vectors `[amount, tender_type, source, hour, day]`. Outliers are isolated in significantly fewer splits (shorter path lengths).
- **Action:** Flags anomalous transactions for administrative review in the audit panel without blocking customer checkouts.

### Feature 4: Inventory Demand Forecasting (Moving Average)
- **Algorithm:** Blended 7-Day (60%) & 30-Day (40%) Moving Average.
- **Runway Days:** $\text{Current Stock} / \text{Daily Velocity}$.
- **Alert Levels:** Flags products as `CRITICAL` ($\le 3$ days), `HIGH` ($\le 7$ days), or `NORMAL`.

---

## 📁 7. Project File Directory & Documentation

```text
asp/
├── backend/
│   ├── app/
│   │   ├── auth/                 # Role-based decorators (@admin_required, etc.)
│   │   ├── models/               # 18 SQLAlchemy Database Models
│   │   ├── routes/               # 12 Modular REST API Blueprints
│   │   ├── services/             # CheckoutService with row-level locks & idempotency
│   │   ├── extensions.py         # Decoupled db, jwt, cors, migrate
│   │   └── __init__.py           # Flask Application Factory
│   ├── config.py                 # Multi-environment configuration
│   ├── requirements.txt          # Python dependencies
│   └── run.py                    # Server launcher
├── frontend/
│   ├── src/
│   │   ├── components/           # Navbar, Footer, Thermal ReceiptModal
│   │   ├── context/              # AuthContext, CartContext
│   │   ├── pages/
│   │   │   ├── Admin/            # AdminDashboard, ProductMgmt, InventoryMgmt, AimlInsights
│   │   │   ├── Customer/         # CustomerHome, ProductCatalog, CartPage, CheckoutPage, MyOrders
│   │   │   ├── Store/            # PosTerminal (DMart cashier interface)
│   │   │   └── Auth/             # Login, Register
│   │   ├── services/             # Axios API client with JWT interceptor
│   │   ├── App.jsx               # React Router navigation tree
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── aiml/
│   ├── sales_prediction.py       # Linear Regression OLS engine
│   ├── recommendation.py         # Popularity ranking engine
│   ├── anomaly_detection.py      # Isolation Forest tree ensemble
│   ├── stock_prediction.py       # Moving Average demand forecaster
│   └── train_models.py           # Standalone verification script
├── database/
│   ├── schema.sql                # Complete MySQL 8.0 DDL schema (18 tables)
│   ├── sample_data_generator.py  # Generates 10,000 orders & 1,000 products
│   └── test_db_connection.py     # Diagnostics utility
├── docs/
│   ├── architecture.md           # System architecture & sequence flow
│   ├── database_design.md        # Complete ERD & 18 tables schema documentation
│   ├── api_documentation.md      # REST API endpoints & JSON payloads
│   ├── testing_report.md         # 35-test Pytest verification report
│   ├── viva_questions_answers.md # 3rd-year engineering viva preparation guide
│   └── presentation_outline.md   # 15-slide PowerPoint presentation outline
└── tests/
    ├── conftest.py               # Shared test fixtures & JWT mock headers
    ├── test_phase1_setup.py      # Infrastructure & model binding tests
    ├── test_auth.py              # Authentication & RBAC tests
    ├── test_products.py          # Catalog & barcode lookup tests
    ├── test_pos.py               # DMart POS retail checkout tests
    ├── test_orders.py            # Online order idempotency & cancellation tests
    └── test_aiml.py              # AIML algorithms & predictive endpoint tests
```

---

## 🎓 8. Academic Deliverables & Viva Prep

All college submission deliverables are ready in the `docs/` folder:
- **Architecture Specification:** [`docs/architecture.md`](file:///c:/Users/aryan/OneDrive/Desktop/asp/docs/architecture.md)
- **Database ERD & Schema:** [`docs/database_design.md`](file:///c:/Users/aryan/OneDrive/Desktop/asp/docs/database_design.md)
- **REST API Documentation:** [`docs/api_documentation.md`](file:///c:/Users/aryan/OneDrive/Desktop/asp/docs/api_documentation.md)
- **Automated Testing Report:** [`docs/testing_report.md`](file:///c:/Users/aryan/OneDrive/Desktop/asp/docs/testing_report.md)
- **Viva Questions & Answers:** [`docs/viva_questions_answers.md`](file:///c:/Users/aryan/OneDrive/Desktop/asp/docs/viva_questions_answers.md)
- **15-Slide Presentation Outline:** [`docs/presentation_outline.md`](file:///c:/Users/aryan/OneDrive/Desktop/asp/docs/presentation_outline.md)

---
*Developed for 3rd-Year Artificial Intelligence & Machine Learning Engineering Major Project Evaluation.*
