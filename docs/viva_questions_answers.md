# SmartFlow – Engineering Viva Examination Q&A Guide

**Target Audience:** 3rd Year AIML / Computer Science Engineering Students  
**Subject:** Major Project / Final Year Evaluation Viva  
**Platform:** SmartFlow – AI-Powered Retail & E-Commerce Management System  

---

## Section 1: System Concept & Full-Stack Architecture

### Q1. What is the core problem that SmartFlow solves?
**Answer:**  
In conventional business setups, brick-and-mortar stores (like DMart) and online e-commerce portals (like Amazon) maintain fragmented software stacks. This causes inventory desynchronization, double allocations, separate transaction records, and poor demand forecasting.  
**SmartFlow** bridges physical retail and digital e-commerce into **one unified database and transaction engine**, sharing centralized inventory across physical branches and fulfillment warehouses, while leveraging predictive machine learning models to forecast sales, detect transaction fraud, and optimize inventory restocks.

### Q2. What technology stack did you choose and why?
**Answer:**  
- **Backend:** Python and Flask with Flask-SQLAlchemy, Flask-JWT-Extended, and Flask-CORS. Python was chosen for seamless integration with mathematical machine learning libraries (Pandas, NumPy, Scikit-learn), while Flask provides a lightweight, modular REST architecture.
- **Frontend:** React.js with Vite, Tailwind CSS, React Router, Axios, and Chart.js. React provides a reactive component model for fast cashier POS interactions and Amazon-style catalog browsing without page reloads.
- **Database:** MySQL 8.0 (with SQLite local fallback mode) via SQLAlchemy ORM, ensuring strict ACID compliance, relational foreign-key integrity, and row-level locking.

---

## Section 2: Database & Transaction Engineering

### Q3. How does SmartFlow prevent overselling and race conditions when multiple customers buy the same item simultaneously?
**Answer:**  
SmartFlow uses **database transactions and row-level locking** via SQLAlchemy's `with_for_update()` method:
```python
inv_record = Inventory.query.filter_by(
    store_id=store_id, product_id=product_id
).with_for_update().first()
```
In SQL, this executes a `SELECT ... FOR UPDATE` statement. This places an exclusive write lock on that specific product's inventory row. Any concurrent transaction attempting to read or modify that same row is forced to wait until the current transaction commits (`db.session.commit()`) or rolls back (`db.session.rollback()`). If stock is insufficient, the transaction rolls back cleanly, ensuring inventory never drops below zero.

### Q4. What is an Idempotency Key, and how did you implement it?
**Answer:**  
An **idempotency key** is a unique client-generated token (UUID) sent in the checkout payload. If a cashier double-clicks the "Complete Bill" button or a network timeout occurs during an online payment, the client replays the exact same request with the same idempotency key.  
Our backend checks `Order.query.filter_by(idempotency_key=key).first()`. If an order with that key already exists, the server returns the previously generated order confirmation **without debiting the customer's payment or deducting inventory a second time**.

---

## Section 3: AIML Algorithms & Mathematics

### Q5. Explain Feature 1: How does your Sales Prediction algorithm work?
**Answer:**  
We implement **Linear Regression using Ordinary Least Squares (OLS)**.  
1. **Data Aggregation:** We query historical daily transaction amounts from the centralized `transactions` table.
2. **Feature Engineering:** We extract calendar features from dates:
   - `trend_index`: Continuous time counter ($t = 0, 1, 2, ...$) to capture secular sales growth.
   - `day_of_week`: Encoded $0$ to $6$ to capture weekend shopping spikes.
   - `day_of_month`: Encoded $1$ to $31$ to capture beginning-of-the-month salary spending surges.
   - `is_weekend`: Binary flag ($1$ for Saturday/Sunday, $0$ otherwise).
3. **Model Formulation:**  
   $$y = \beta_0 + \beta_1 \cdot \text{trend} + \beta_2 \cdot \text{dow} + \beta_3 \cdot \text{dom} + \beta_4 \cdot \text{weekend} + \epsilon$$
4. **Evaluation Metrics:** We evaluate performance using:
   - **Mean Absolute Error (MAE):** $\text{MAE} = \frac{1}{n} \sum |y_i - \hat{y}_i|$ (measures average magnitude of errors in Rupees).
   - **Root Mean Squared Error (RMSE):** $\text{RMSE} = \sqrt{\frac{1}{n} \sum (y_i - \hat{y}_i)^2}$ (penalizes large outlier misses).
   - **Coefficient of Determination ($R^2$):** $R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$ (percentage of sales variance explained by the model, achieving $\approx 0.85$).

### Q6. Why did you choose Popularity-Based Recommendations instead of Deep Collaborative Filtering?
**Answer:**  
As a 3rd-year engineering project, popularity-based frequency ranking provides three distinct advantages:
1. **Cold Start Immunity:** New customers with zero prior purchase history immediately receive relevant recommendations of verified top-selling items.
2. **Fast Low-Latency Queries:** Aggregating `order_items` purchase counts executes in sub-millisecond database time without requiring GPU training clusters.
3. **Real-world Business Applicability:** In retail staples (DMart grocery items like sugar, flour, oil), high-frequency items represent 80% of repeat customer purchases (Pareto principle).

### Q7. Explain Feature 3: How does the Isolation Forest algorithm detect unusual transactions?
**Answer:**  
**Isolation Forest (iForest)** isolates anomalies rather than profiling normal data points:
1. **Concept:** Anomalous points (e.g., an abnormal ₹95,000 transaction at a grocery register) have attribute values far away from normal transactions. Therefore, when random axis-aligned splits are chosen recursively to partition the data, anomalies are isolated in **substantially fewer tree splits** (shorter path lengths) compared to normal transactions.
2. **Path Length & Anomaly Score:**  
   The anomaly score $s(x, n)$ for a transaction $x$ over an ensemble of $m$ Isolation Trees is:
   $$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
   Where $E(h(x))$ is the average path length of $x$, and $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree:
   $$c(n) = 2 \ln(n - 1) + 0.5772156649 - \frac{2(n - 1)}{n}$$
3. **Thresholding:**
   - If $s \to 1.0$: the path length is extremely short $\implies$ **Statistical Anomaly**.
   - If $s < 0.5$: the point has a long path deep in the tree $\implies$ **Normal Transaction**.
4. **Action:** The system flags anomalies for **Admin Audit Review** in the dashboard without blocking the customer at checkout.

### Q8. Explain Feature 4: How does your Moving Average demand forecast estimate stock depletion?
**Answer:**  
We use a **blended 7-day and 30-day Moving Average daily velocity rate**:
$$\text{Daily Demand Rate} = 0.6 \times \left(\frac{\text{Sales}_{7d}}{7}\right) + 0.4 \times \left(\frac{\text{Sales}_{30d}}{30}\right)$$
We weigh the recent 7 days at 60% to capture short-term demand surges, and 30 days at 40% for seasonal stability.  
$$\text{Days Remaining} = \frac{\text{Current Stock Quantity}}{\text{Daily Demand Rate}}$$
- If $\text{Days Remaining} \le 3$: Flagged as **`CRITICAL`** priority.
- If $\text{Days Remaining} \le 7$: Flagged as **`HIGH`** priority.
- If $\text{Days Remaining} > 7$: Flagged as **`NORMAL`**.

---

## Section 4: Security, Roles & Enterprise Architecture

### Q9. How is Role-Based Access Control (RBAC) enforced in SmartFlow?
**Answer:**  
We implement custom Python decorators (`@admin_required`, `@employee_required`, `@customer_required`) on top of Flask-JWT-Extended:
1. When a user logs in, their identity and `role` are signed into a JWT access token using HMAC-SHA256.
2. Protected endpoints inspect the token payload.
3. If an unauthorized user attempts an operation (for example, a Customer attempting to create a product or trigger an Isolation Forest audit scan), the decorator intercepts the request and terminates with HTTP `403 Forbidden`.

### Q10. What are the engineering boundaries and realistic constraints of this project?
**Answer:**  
- **Financial Simulation:** Real-world payment gateway integrations (Razorpay, Stripe) require commercial business registrations and merchant banking accounts. To remain compliant for an academic project, payments are simulated safely while capturing all standard banking payload fields (payment method, gateway reference, approval timestamps).
- **Scale:** SmartFlow is engineered and verified for realistic retail store operations (tested with 1,000 products, 10,000 orders, and concurrent row locks), not multi-region hyper-scale clusters requiring Apache Kafka or Redis distributed caches.
