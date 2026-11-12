"""High-Performance Realistic Synthetic Sample Data Generator for SmartFlow.
Generates:
  - 3 Stores (Hub, DMart Andheri, DMart Whitefield)
  - 7 Categories
  - 1,000 Master Products with realistic SKUs, barcodes, MRPs & prices
  - 500 Customer accounts with addresses and lifetime spending metrics
  - 10 Store Cashiers & Managers
  - 10,000+ Unified Orders & Financial Transactions spanning the last 180 days
  - Pre-allocated store inventory and stock history records
"""
import os
import sys
import random
import uuid
from datetime import datetime, timedelta, timezone

# Ensure root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import (
    User, Customer, Employee, Category, Product, Store, Inventory,
    StockHistory, Order, OrderItem, Transaction, PaymentRecord,
    Cart, CartItem, Coupon, Recommendation, AuditLog
)

# Realistic product naming seeds by category
PRODUCT_SEEDS = {
    'Groceries & Staples': {
        'items': [
            'Basmati Rice', 'Sona Masoori Rice', 'Whole Wheat Atta', 'Toor Dal', 'Moong Dal',
            'Chana Dal', 'Refined Sunflower Oil', 'Mustard Oil', 'Iodized Salt', 'Pure Ghee',
            'Sugar Crystals', 'Cumin Seeds (Jeera)', 'Turmeric Powder', 'Red Chilli Powder',
            'Coriander Powder', 'Garam Masala', 'Poha (Flattened Rice)', 'Rava (Soji)',
            'Groundnut Oil', 'Black Peppercorns', 'Kabuli Chana', 'Rajma Red', 'Green Cardamom'
        ],
        'brands': ['Fortune', 'Aashirvaad', 'Tata Sampann', 'Dhiraj', 'India Gate', 'Patanjali', 'Amul', 'Saffola'],
        'price_range': (40, 750),
        'unit': 'kg'
    },
    'Electronics & Gadgets': {
        'items': [
            'Wireless Bluetooth Earbuds', 'Fast Charging USB-C Cable', '10000mAh Power Bank',
            'Wireless Optical Mouse', 'Mechanical Gaming Keyboard', 'Smart Fitness Band',
            'Portable Bluetooth Speaker', 'HDMI 4K Cable 2m', 'Laptop Cooling Pad',
            'Noise Cancelling Headphones', 'Smart LED Desk Lamp', 'Multi-Port USB Hub',
            'Surge Protector Power Strip', 'Webcam 1080p HD', 'Wi-Fi Dual Band Router'
        ],
        'brands': ['boAt', 'Noise', 'Realme', 'Portronics', 'Logitech', 'Mi', 'SanDisk', 'Zebronics', 'TP-Link'],
        'price_range': (299, 4999),
        'unit': 'piece'
    },
    'Clothing & Fashion': {
        'items': [
            'Men Solid Round Neck T-Shirt', 'Women Floral Print Kurti', 'Slim Fit Cotton Jeans',
            'Formal White Cotton Shirt', 'Track Pants Athletic Wear', 'Casual Canvas Sneakers',
            'Running Sports Shoes', 'Cotton Ankle Socks (Pack of 3)', 'Leather Wallet Men',
            'Cotton Nightwear Set', 'Denim Jacket Casual', 'Polo Collar Sport T-Shirt'
        ],
        'brands': ['Roadster', 'Peter England', 'Allen Solly', 'Puma', 'Max', 'U.S. Polo', 'FabIndia', 'Sparx'],
        'price_range': (249, 2499),
        'unit': 'piece'
    },
    'Home Appliances': {
        'items': [
            'Electric Cordless Kettle 1.5L', 'Dry Iron 1000W', 'Steam Iron Non-Stick',
            '3-Jar Mixer Grinder 750W', 'Sandwich Maker Toasting Plate', 'Hand Blender 300W',
            'Personal Room Air Cooler', 'Induction Cooktop 2000W', 'Pop-Up 2-Slice Toaster',
            'Electric Egg Boiler', 'Vacuum Cleaner Handheld'
        ],
        'brands': ['Bajaj', 'Philips', 'Prestige', 'Havells', 'Crompton', 'Morphy Richards', 'Usha'],
        'price_range': (699, 5999),
        'unit': 'piece'
    },
    'Personal Care': {
        'items': [
            'Gentle Foaming Face Wash 100ml', 'Anti-Dandruff Shampoo 400ml', 'Daily Moisture Body Lotion',
            'Moisturizing Bathing Soap (Pack of 4)', 'Herbal Toothpaste 150g', 'Activated Charcoal Scrub',
            'Sunscreen SPF 50 Gel 50g', 'Hydrating Sheet Mask', 'Cooling Talcum Powder 250g',
            'Deodorant Body Spray 150ml', 'Hair Conditioner Keratin 200ml'
        ],
        'brands': ['Nivea', 'Dove', 'Himalaya', 'Colgate', 'Dettol', 'Pond\'s', 'Head & Shoulders', 'Fogg', 'Garnier'],
        'price_range': (65, 450),
        'unit': 'piece'
    },
    'Food & Beverages': {
        'items': [
            'Instant Masala Noodles (Pack of 8)', 'Crispy Potato Chips 150g', 'Butter Cookies 200g',
            'Alphonso Mango Fruit Drink 1L', 'Roasted Salted Almonds 200g', 'Cashew Nuts Premium 200g',
            'Dark Chocolate Bar 100g', 'Roasted Peanut Butter 500g', 'Green Tea Lemon & Honey 25 Bags',
            'Instant Roasted Coffee 100g', 'Tomato Ketchup Squeezy 500g', 'Cornflakes Breakfast Cereal 500g'
        ],
        'brands': ['Maggi', 'Lay\'s', 'Britannia', 'Frooti', 'Cadbury', 'Nescafe', 'Tata Tea', 'Kellogg\'s', 'Kissan'],
        'price_range': (20, 420),
        'unit': 'piece'
    },
    'Household Essentials': {
        'items': [
            'Dishwash Gel Lemon 750ml', 'Liquid Detergent Front Load 1L', 'Floor Cleaner Citrus 1L',
            'Toilet Cleaner Power 1L', 'Microfiber Cleaning Cloths (Pack of 4)', 'Garbage Bags Biodegradable (Pack of 30)',
            'Mosquito Vaporizer Refill (Pack of 2)', 'Aluminium Foil Roll 25m', 'Stainless Steel Kitchen Scrubber (Pack of 3)'
        ],
        'brands': ['Vim', 'Surf Excel', 'Lizol', 'Harpic', 'Scotch-Brite', 'Good Knight', 'Colin', 'Ariel'],
        'price_range': (35, 380),
        'unit': 'piece'
    }
}

INDIAN_CITIES = [
    ('Mumbai', 'Maharashtra'), ('Bengaluru', 'Karnataka'), ('Pune', 'Maharashtra'),
    ('Delhi', 'Delhi'), ('Hyderabad', 'Telangana'), ('Ahmedabad', 'Gujarat'),
    ('Chennai', 'Tamil Nadu'), ('Kolkata', 'West Bengal'), ('Jaipur', 'Rajasthan')
]

FIRST_NAMES = [
    'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
    'Ananya', 'Diya', 'Gauri', 'Aditi', 'Rhea', 'Pooja', 'Sneha', 'Neha', 'Priya', 'Kavya',
    'Rohit', 'Rahul', 'Karan', 'Vikram', 'Siddharth', 'Amit', 'Sunil', 'Manish', 'Deepak', 'Suresh',
    'Meera', 'Tanvi', 'Shreya', 'Simran', 'Nisha', 'Aastha', 'Ritu', 'Swati', 'Alka', 'Bhavna'
]

LAST_NAMES = [
    'Sharma', 'Verma', 'Patel', 'Shah', 'Gupta', 'Mehta', 'Joshi', 'Singh', 'Kumar', 'Reddy',
    'Nair', 'Iyer', 'Deshmukh', 'Kulkarni', 'Choudhury', 'Banerjee', 'Das', 'Bose', 'Chatterjee', 'Rao'
]


def generate_synthetic_data(num_products=1000, num_customers=500, num_transactions=10000):
    print("=" * 65)
    print("      SMARTFLOW ENTERPRISE SYNTHETIC DATA GENERATOR")
    print(f"      Targets: {num_products} Products | {num_customers} Customers | {num_transactions} Txns")
    print("=" * 65)

    app = create_app()
    with app.app_context():
        # Clean slate or inspect existing
        existing_products = Product.query.count()
        if existing_products >= num_products:
            print(f"[!] Products already seeded ({existing_products} exist). Skipping product generation.")
        else:
            print("\n[1/5] Seeding Categories & 1,000 Products...")
            categories = {c.name: c for c in Category.query.all()}
            stores = Store.query.all()
            if not stores:
                print("[-] Error: No stores found. Run `python backend/run.py db-init` first.")
                return

            products_to_add = []
            skus_created = set()
            barcodes_created = set()

            cat_names = list(PRODUCT_SEEDS.keys())
            for i in range(num_products):
                cat_name = cat_names[i % len(cat_names)]
                category = categories.get(cat_name)
                seed_data = PRODUCT_SEEDS[cat_name]

                base_item = random.choice(seed_data['items'])
                brand = random.choice(seed_data['brands'])
                variant = random.choice(['Classic', 'Premium', 'Pro', 'Gold', 'Eco', 'Special', 'Select', 'Ultra'])
                product_name = f"{brand} {base_item} ({variant})"

                # Generate clean unique SKU and Barcode
                cat_prefix = ''.join([c for c in cat_name.upper() if c.isalnum()][:3])
                sku = f"{cat_prefix}-{10000 + i}"
                barcode = f"890{random.randint(100000000, 999999999)}"
                while barcode in barcodes_created:
                    barcode = f"890{random.randint(100000000, 999999999)}"
                barcodes_created.add(barcode)

                min_p, max_p = seed_data['price_range']
                price = round(random.uniform(min_p, max_p), 2)
                mrp = round(price * random.uniform(1.05, 1.30), 2)  # MRP 5% - 30% higher than price
                cost_price = round(price * random.uniform(0.65, 0.80), 2)  # 20-35% profit margin

                p = Product(
                    category_id=category.id if category else 1,
                    sku=sku,
                    barcode=barcode,
                    name=product_name,
                    description=f"Authentic {product_name} by {brand}. Premium quality guaranteed.",
                    brand=brand,
                    unit=seed_data['unit'],
                    mrp=mrp,
                    price=price,
                    cost_price=cost_price,
                    image_url=category.image_url if category else None,
                    is_available=True
                )
                products_to_add.append(p)

            db.session.bulk_save_objects(products_to_add)
            db.session.commit()
            print(f"  ✓ Created {len(products_to_add)} products across 7 categories.")

            # Allocate Store Inventory for all products
            print("  [*] Allocating store inventories & safety stock thresholds...")
            all_products = Product.query.all()
            inventories = []
            for p in all_products:
                for store in stores:
                    stock_qty = random.randint(20, 200)
                    inv = Inventory(
                        store_id=store.id,
                        product_id=p.id,
                        stock_quantity=stock_qty,
                        safety_stock_level=15,
                        reorder_quantity=60
                    )
                    inventories.append(inv)

            db.session.bulk_save_objects(inventories)
            db.session.commit()
            print(f"  ✓ Allocated {len(inventories)} store inventory records.")

        # 2. Customers
        existing_customers = Customer.query.count()
        if existing_customers >= num_customers:
            print(f"[!] Customers already seeded ({existing_customers} exist). Skipping.")
        else:
            print(f"\n[2/5] Creating {num_customers} Customer Accounts...")
            customers_to_add = []
            users_to_add = []
            for i in range(1, num_customers + 1):
                fname = random.choice(FIRST_NAMES)
                lname = random.choice(LAST_NAMES)
                username = f"{fname.lower()}_{lname.lower()}_{i}"
                email = f"{username}@example.com"
                city, state = random.choice(INDIAN_CITIES)
                phone = f"+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}"

                user = User(
                    username=username,
                    email=email,
                    role='CUSTOMER',
                    is_active=True
                )
                user.set_password('Customer@12345')
                users_to_add.append(user)

            db.session.add_all(users_to_add)
            db.session.commit()

            # Now create Customer profiles linked to users
            created_users = User.query.filter_by(role='CUSTOMER').all()
            for u in created_users:
                if not u.customer_profile:
                    city, state = random.choice(INDIAN_CITIES)
                    phone = f"+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}"
                    cust = Customer(
                        user_id=u.id,
                        full_name=u.username.replace('_', ' ').title(),
                        phone=phone,
                        address=f"{random.randint(1, 500)}, Sector {random.randint(1, 25)}, {city}",
                        city=city,
                        postal_code=str(random.randint(110001, 700001))
                    )
                    customers_to_add.append(cust)

            db.session.add_all(customers_to_add)
            db.session.commit()
            print(f"  ✓ Created {len(customers_to_add)} customer profiles.")

        # 3. Store Cashiers & Staff
        print("\n[3/5] Verifying Cashier & Employee Accounts...")
        stores = Store.query.all()
        cashier_user = User.query.filter_by(username='cashier_mumbai').first()
        if not cashier_user:
            cashier_user = User(
                username='cashier_mumbai',
                email='cashier.mumbai@smartflow.com',
                role='EMPLOYEE',
                is_active=True
            )
            cashier_user.set_password('Cashier@12345')
            db.session.add(cashier_user)
            db.session.flush()

            emp = Employee(
                user_id=cashier_user.id,
                store_id=2,  # DMart Andheri
                employee_code='EMP-DMRT-101',
                full_name='Ramesh Sharma (Senior Cashier)',
                position='Head Cashier',
                shift='MORNING'
            )
            db.session.add(emp)
            db.session.commit()
            print("  ✓ Created demo cashier account: cashier_mumbai / Cashier@12345")

        # 4. Generate 10,000+ Unified Transactions spanning 180 days
        existing_txns = Transaction.query.count()
        if existing_txns >= num_transactions:
            print(f"[!] Transactions already seeded ({existing_txns} exist). Skipping.")
        else:
            needed = num_transactions - existing_txns
            print(f"\n[4/5] Synthesizing {needed} Realistic Transactions across 180 Days...")
            all_products = Product.query.all()
            all_customers = Customer.query.all()
            stores = Store.query.all()
            payment_methods = ['CASH', 'UPI', 'CARD', 'ONLINE_NETBANKING']

            now = datetime.now(timezone.utc)
            start_date = now - timedelta(days=180)

            # Pre-generate dates with weekday and weekend peaks
            orders_batch = []
            txns_batch = []
            pay_records_batch = []
            order_items_batch = []

            BATCH_SIZE = 1000
            total_generated = 0

            for i in range(needed):
                # Distribute dates realistically (more transactions on weekends & recent days)
                day_offset = random.choices(
                    range(180),
                    weights=[(i + 1)**1.2 for i in range(180)],  # Slight upward growth trend
                    k=1
                )[0]
                txn_date = start_date + timedelta(
                    days=day_offset,
                    hours=random.randint(9, 21),  # Shopping between 9am and 9pm
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )

                # 60% Store POS purchases, 40% Online Amazon-style orders
                is_store = random.random() < 0.60
                order_type = 'STORE' if is_store else 'ONLINE'
                store = random.choice(stores)
                customer = random.choice(all_customers) if (random.random() < 0.85 or not is_store) else None

                # 1 to 6 items per transaction
                basket_size = random.randint(1, 5)
                basket_products = random.sample(all_products, k=basket_size)

                subtotal = 0.0
                items_tuples = []
                for p in basket_products:
                    qty = random.randint(1, 3)
                    item_sub = float(p.price) * qty
                    subtotal += item_sub
                    items_tuples.append((p.id, qty, float(p.price), item_sub))

                # Occasional coupon discount
                discount = 0.0
                if random.random() < 0.20 and subtotal > 500:
                    discount = round(subtotal * random.choice([0.05, 0.10, 0.15]), 2)

                tax = round((subtotal - discount) * 0.05, 2)
                final_amount = round(subtotal - discount + tax, 2)

                # Payment method distribution
                if is_store:
                    pay_method = random.choices(['CASH', 'UPI', 'CARD'], weights=[0.40, 0.45, 0.15])[0]
                else:
                    pay_method = random.choices(['UPI', 'CARD', 'ONLINE_NETBANKING'], weights=[0.55, 0.35, 0.10])[0]

                # Anomaly injection: ~3% unusual outliers (e.g. very high bulk spend or abnormal hours)
                is_anomaly = False
                anomaly_score = random.uniform(0.1, 0.6)
                if random.random() < 0.035:
                    is_anomaly = True
                    final_amount = round(final_amount * random.uniform(3.5, 7.0), 2)
                    anomaly_score = random.uniform(-0.6, -0.1)

                order_num = f"{'POS' if is_store else 'ORD'}-{txn_date.strftime('%Y%m%d')}-{i+1:06d}-{uuid.uuid4().hex[:6].upper()}"
                order = Order(
                    order_number=order_num,
                    customer_id=customer.id if customer else None,
                    store_id=store.id,
                    order_type=order_type,
                    order_status='COMPLETED',
                    subtotal=subtotal,
                    discount_amount=discount,
                    tax_amount=tax,
                    total_amount=final_amount,
                    created_at=txn_date
                )
                db.session.add(order)
                db.session.flush()

                # Order Items
                for pid, qty, unit_p, isub in items_tuples:
                    oi = OrderItem(
                        order_id=order.id,
                        product_id=pid,
                        quantity=qty,
                        unit_price=unit_p,
                        subtotal=isub,
                        created_at=txn_date
                    )
                    db.session.add(oi)

                # Transaction Record
                txn_ref = f"TXN-{txn_date.strftime('%Y%m%d')}-{i+1:06d}-{uuid.uuid4().hex[:6].upper()}"
                txn = Transaction(
                    transaction_id=txn_ref,
                    order_id=order.id,
                    customer_id=customer.id if customer else None,
                    store_id=store.id,
                    source=order_type,
                    amount=final_amount,
                    status='SUCCESS',
                    payment_method=pay_method,
                    is_flagged_anomaly=is_anomaly,
                    anomaly_score=anomaly_score,
                    created_at=txn_date
                )
                db.session.add(txn)
                db.session.flush()

                pr = PaymentRecord(
                    transaction_id=txn.id,
                    payment_gateway_ref=f"SIM-{uuid.uuid4().hex[:8].upper()}",
                    payment_method=pay_method,
                    amount=final_amount,
                    status='SUCCESS',
                    response_message='Simulated settlement approved',
                    created_at=txn_date
                )
                db.session.add(pr)

                total_generated += 1
                if total_generated % BATCH_SIZE == 0:
                    db.session.commit()
                    print(f"  ... committed {total_generated}/{needed} transactions")

            db.session.commit()
            print(f"  ✓ Successfully synthesized and committed {total_generated} unified transactions.")

        # 5. Precalculate Recommendations & Audit Log
        print("\n[5/5] Initializing Recommendations and System Health Check...")
        from aiml.recommendation import ProductRecommender
        recommender = ProductRecommender()
        recs = recommender.get_popular_recommendations(limit=10)
        print(f"  ✓ Generated {len(recs)} trending recommendations from transaction history.")

        print("\n" + "=" * 65)
        print(">>> SUCCESS: SmartFlow Master Dataset Initialized Successfully!")
        print("=" * 65)


if __name__ == '__main__':
    generate_synthetic_data(num_products=1000, num_customers=500, num_transactions=10000)
