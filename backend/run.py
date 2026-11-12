"""Application entrypoint and CLI manager for SmartFlow."""
import os
import sys

# Ensure root directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import (
    User, Customer, Employee, Category, Product, Store, Inventory,
    StockHistory, Order, OrderItem, Transaction, PaymentRecord,
    Cart, CartItem, Coupon, Recommendation, AuditLog
)

app = create_app(os.getenv('FLASK_ENV', 'development'))


def seed_base_data():
    """Seed initial stores, categories, coupons, and superadmin user."""
    with app.app_context():
        # 1. Stores
        if Store.query.count() == 0:
            hub = Store(
                id=1,
                store_code='HUB-001',
                name='SmartFlow Central Warehouse & E-Commerce Hub',
                location='Sector 18, Industrial Area',
                city='Mumbai',
                phone='+91 98765 00001'
            )
            store1 = Store(
                id=2,
                store_code='DMRT-101',
                name='SmartFlow DMart Retail Store - Andheri West',
                location='SV Road, Andheri West',
                city='Mumbai',
                phone='+91 98765 00002'
            )
            store2 = Store(
                id=3,
                store_code='DMRT-102',
                name='SmartFlow DMart Retail Store - Whitefield',
                location='ITPL Main Road, Whitefield',
                city='Bengaluru',
                phone='+91 98765 00003'
            )
            db.session.add_all([hub, store1, store2])
            db.session.commit()
            print("✓ Seeded default Stores (HUB-001, DMRT-101, DMRT-102)")

        # 2. Categories
        if Category.query.count() == 0:
            categories_data = [
                ('Groceries & Staples', 'Rice, Dal, Atta, Cooking Oils, Spices, Grains', 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80'),
                ('Electronics & Gadgets', 'Smartphones, Audio, Cables, Laptops, Accessories', 'https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&w=400&q=80'),
                ('Clothing & Fashion', 'Men, Women, Kids Apparel and Footwear', 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=400&q=80'),
                ('Home Appliances', 'Kitchen appliances, Coolers, Vacuums, Irons', 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=400&q=80'),
                ('Personal Care', 'Skin care, Shampoos, Oral care, Perfumes', 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=400&q=80'),
                ('Food & Beverages', 'Packaged snacks, Biscuits, Tea, Coffee, Juices', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80'),
                ('Household Essentials', 'Cleaners, Detergents, Mops, Kitchenware', 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=400&q=80')
            ]
            for cat_id, (name, desc, img) in enumerate(categories_data, start=1):
                c = Category(id=cat_id, name=name, description=desc, image_url=img)
                db.session.add(c)
            db.session.commit()
            print("✓ Seeded default Categories (7 core retail categories)")

        # 3. Coupons
        if Coupon.query.count() == 0:
            from datetime import datetime, timezone, timedelta
            now = datetime.now(timezone.utc)
            c1 = Coupon(
                code='WELCOME50',
                discount_percent=10.0,
                max_discount_amount=200.0,
                min_order_amount=500.0,
                usage_limit=10000,
                expires_at=now + timedelta(days=730)
            )
            c2 = Coupon(
                code='FESTIVE20',
                discount_percent=20.0,
                max_discount_amount=500.0,
                min_order_amount=1200.0,
                usage_limit=5000,
                expires_at=now + timedelta(days=730)
            )
            c3 = Coupon(
                code='SUPERMART5',
                discount_percent=5.0,
                max_discount_amount=100.0,
                min_order_amount=300.0,
                usage_limit=50000,
                expires_at=now + timedelta(days=730)
            )
            db.session.add_all([c1, c2, c3])
            db.session.commit()
            print("✓ Seeded standard promotional coupons")

        # 4. Superadmin User
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@smartflow.com',
                role='ADMIN',
                is_active=True
            )
            admin_user.set_password('Admin@12345')
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Created default superadmin user: admin / Admin@12345")


if __name__ == '__main__':
    args = sys.argv[1:]
    
    if len(args) > 0 and args[0] == 'db-init':
        print("\n=======================================================")
        print("  SMARTFLOW DATABASE INITIALIZATION")
        print(f"  Target URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("=======================================================")
        with app.app_context():
            db.create_all()
            print("✓ Created all 18 database tables successfully.")
            seed_base_data()
            print("✓ Base database tables and seed records verified.\n")
    else:
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        print(f"\n🚀 SmartFlow API Server starting on http://localhost:{port}")
        print(f"   Database: {app.config['SQLALCHEMY_DATABASE_URI']}\n")
        app.run(host=host, port=port, debug=app.config.get('DEBUG', True))
