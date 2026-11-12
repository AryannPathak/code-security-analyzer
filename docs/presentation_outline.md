# SmartFlow – 15-Slide Presentation Outline for Major Project Defense

**Project Name:** SmartFlow – AI-Powered Retail & E-Commerce Management System  
**Presentation Time:** 12 to 15 Minutes + 5 Minutes Q&A  
**Student Level:** 3rd Year AIML Engineering  

---

### Slide 1: Title & Candidate Information
- **Title:** SMARTFLOW: AI-Powered Retail & E-Commerce Management System
- **Subtitle:** Unifying Physical Store POS and Digital E-Commerce with Predictive Machine Learning
- **Presenter:** [Student Name] – 3rd Year B.Tech / B.E. (Artificial Intelligence & Machine Learning)
- **Academic Year:** 2025–2026

---

### Slide 2: Project Motivation & Industry Context
- **The Modern Retail Dilemma:** Traditional retail chains maintain separate legacy software for physical billing and online portals.
- **Consequences:** Inventory mismatch, double allocations, disparate financial reporting, and inability to forecast demand across channels.
- **SmartFlow Vision:** A single, centralized platform combining the in-store physical Point-of-Sale speed of **DMart** with the digital e-commerce customer experience of **Amazon**.

---

### Slide 3: Objectives & Key Capabilities
- **Unified Inventory:** Centralized real-time tracking across physical stores and fulfillment hubs.
- **Dual-Channel Checkout:** In-store POS cashier terminal + Amazon-style online cart and checkout.
- **Centralized Ledger:** Both online orders and store bills stored in one single transaction ledger.
- **Applied AIML:** Beginner-to-intermediate machine learning algorithms for sales prediction, recommendations, fraud anomaly detection, and stock forecasting.

---

### Slide 4: Technology Stack
- **Frontend:** React 18, Vite 5, Tailwind CSS, React Router 6, Axios, Chart.js, Lucide Icons.
- **Backend:** Python, Flask, Flask-SQLAlchemy ORM, Flask-JWT-Extended, Flask-CORS.
- **Database:** MySQL 8.0 (with SQLite local fallback mode), strict ACID compliance.
- **AIML Pipeline:** Pandas, NumPy, Scikit-learn, Matplotlib (with platform-safe pure-Python mathematical fallbacks).
- **Testing:** Pytest, Postman, automated database concurrency tests.

---

### Slide 5: Application User Roles & Access Control
- **1. Master Administrator:** Catalog CRUD, store management, transaction exports, AIML controls, system audit logs.
- **2. Store Cashier (Employee):** DMart POS billing interface, barcode scanning, simulated cash/UPI/card tender, thermal receipt printing.
- **3. Online Customer:** Product search, category filters, cart stepper, coupon application, order placement, real-time status tracking, self-service cancellation.

---

### Slide 6: Database Architecture (18 Normalized Tables)
- **Normalized Schema:** 3NF design ensuring zero data redundancy.
- **Key Entity Groups:**
  - *Identity:* `users`, `customers`, `employees`.
  - *Catalog & Inventory:* `categories`, `products`, `stores`, `inventory`, `stock_history`.
  - *Sales & Finance:* `orders`, `order_items`, `transactions`, `payment_records`, `coupons`, `returns`.
  - *AIML & Audit:* `cart`, `cart_items`, `recommendations`, `audit_logs`.

---

### Slide 7: DMart Physical Retail POS Terminal
- High-speed cashier interface designed for keyboard and barcode scanner workflows.
- Instant item lookup by standard numeric barcode (`890...`) or SKU.
- Automated subtotal, promotional coupon validation, and 5% GST tax calculation.
- Instant printable thermal receipt modal with bill numbers and store details.
- Immediate store-specific stock deduction upon tender confirmation.

---

### Slide 8: Amazon-Style Digital E-Commerce Storefront
- Clean responsive storefront with hero promo banners, category pills, and search filters.
- AI-recommended product carousels based on aggregate customer purchase frequency.
- Interactive shopping cart with live quantity steppers and subtotal breakdowns.
- Simulated payment methods: UPI ID simulation, credit/debit card, and netbanking.
- "My Orders" customer portal with order tracking timeline and automated cancellation refund processing.

---

### Slide 9: Centralized Financial Transactions & Concurrency
- **Centralized Ledger:** Single schema capturing `source` (`'STORE'` vs `'ONLINE'`).
- **Row-Level Locking:** Prevents inventory overselling race conditions using `SELECT ... FOR UPDATE` (`with_for_update()`).
- **Idempotency Keys:** Client-generated tokens guarantee network timeouts or double clicks never result in duplicate billing or duplicate inventory deductions.
- **Audit Logging:** Every critical transaction, refund, and product update is permanently logged.

---

### Slide 10: AIML Feature 1 – Sales Prediction (Linear Regression)
- **Algorithm:** Ordinary Least Squares (OLS) Linear Regression.
- **Objective:** Forecast future daily sales revenue across the retail chain.
- **Features Extracted:** Date trend index ($t$), day of week, day of month, weekend indicator.
- **Evaluation Metrics:**
  - Mean Absolute Error (MAE): ₹1,279.17
  - Root Mean Squared Error (RMSE): ₹1,506.71
  - Coefficient of Determination ($R^2$): **0.8519** (85.2% variance explained).
- **Dashboard Integration:** Interactive 7-day future forecast and actual-vs-predicted Chart.js graph.

---

### Slide 11: AIML Feature 2 – Product Recommendations
- **Algorithm:** Popularity-Based Collaborative Frequency Ranking.
- **Objective:** Recommend top-performing products to visitors and online shoppers.
- **Implementation:** Real-time frequency counting of historical line items in `order_items`.
- **Advantages:** Eliminates cold-start problem for new shoppers; highly relevant for fast-moving consumer goods (FMCG).

---

### Slide 12: AIML Feature 3 – Unusual Transaction Detection
- **Algorithm:** Isolation Forest (iForest).
- **Objective:** Identify statistically abnormal transaction outliers for audit review.
- **Mathematical Principle:** Anomalous data points require fewer random tree partitions (shorter path lengths) to isolate than dense normal transactions.
- **Result:** Scanned 10,000 real-world transactions and flagged 400 statistical outliers for Admin review without disrupting customer checkout.

---

### Slide 13: AIML Feature 4 – Inventory Demand Forecasting
- **Algorithm:** Blended 7-Day & 30-Day Moving Average.
- **Formula:** $\text{Daily Velocity} = 0.6 \times (\text{Sales}_{7d}/7) + 0.4 \times (\text{Sales}_{30d}/30)$.
- **Runway Days:** $\text{Stock Quantity} / \text{Daily Velocity}$.
- **Decision Engine:** Automatically triggers `CRITICAL` ($\le 3$ days), `HIGH` ($\le 7$ days), and `NORMAL` restock warnings to store managers.

---

### Slide 14: Automated Testing & Verification
- **Testing Framework:** Pytest 9.2.0 automated test suite.
- **Test Results:** **35 / 35 Tests Passed (100% Pass Rate)** in 19.4 seconds.
- **Coverage Areas:**
  - Database schema & model bindings.
  - JWT authentication & Role-Based Access Control.
  - Catalog search & barcode scanning.
  - DMart POS billing & receipt data integrity.
  - Online order idempotency & cancellation stock refunds.
  - All 4 AIML algorithms and REST endpoints.

---

### Slide 15: Conclusion & Future Work
- **Summary:** Successfully built a full-stack, enterprise-grade retail platform uniting physical POS and digital e-commerce with verified AIML models.
- **Key Takeaways:** Real-world mastery of ACID transactions, row-level locks, RESTful APIs, and practical applied machine learning.
- **Future Roadmap:** Multi-region warehouse distribution algorithms, barcode camera scanner WebRTC integration, and dynamic demand pricing.
- **Thank you! Questions & Discussion.**
