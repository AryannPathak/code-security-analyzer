"""Shared Pytest Fixtures for SmartFlow Test Suite."""
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import (
    User, Customer, Employee, Category, Product, Store, Inventory,
    StockHistory, Order, OrderItem, Transaction, PaymentRecord,
    Cart, CartItem, Coupon, Recommendation, AuditLog
)
from flask_jwt_extended import create_access_token


@pytest.fixture
def app():
    """Create Flask application configured for testing with in-memory SQLite."""
    os.environ['FLASK_ENV'] = 'testing'
    test_app = create_app('testing')
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test HTTP client."""
    return app.test_client()


@pytest.fixture
def sample_data(app):
    """Seed test database with baseline store, category, products, and users."""
    with app.app_context():
        # 1. Admin User
        admin_user = User(
            username='test_admin',
            email='admin@testsmartflow.com',
            role='ADMIN',
            is_active=True
        )
        admin_user.set_password('Admin@12345')
        db.session.add(admin_user)

        # 2. Store & Employee User
        store = Store(
            store_code='STR-MUM-01',
            name='DMart Flagship Mumbai',
            location='Malad West',
            city='Mumbai',
            phone='+91 22 2844 1100',
            is_active=True
        )
        db.session.add(store)
        db.session.flush()

        emp_user = User(
            username='test_cashier',
            email='cashier@testsmartflow.com',
            role='EMPLOYEE',
            is_active=True
        )
        emp_user.set_password('Cashier@12345')
        db.session.add(emp_user)
        db.session.flush()

        employee = Employee(
            user_id=emp_user.id,
            store_id=store.id,
            employee_code='EMP-001',
            full_name='Vikram Shinde',
            position='Cashier',
            shift='MORNING'
        )
        db.session.add(employee)

        # 3. Customer User
        cust_user = User(
            username='test_customer',
            email='customer@testsmartflow.com',
            role='CUSTOMER',
            is_active=True
        )
        cust_user.set_password('Customer@12345')
        db.session.add(cust_user)
        db.session.flush()

        customer = Customer(
            user_id=cust_user.id,
            full_name='Aarav Mehta',
            phone='9876543210',
            address='123 Marine Drive',
            city='Mumbai'
        )
        db.session.add(customer)

        # 4. Category
        category = Category(
            name='Groceries & Staples',
            description='Everyday food and cooking essentials'
        )
        db.session.add(category)
        db.session.flush()

        # 5. Products & Store Inventory
        prod1 = Product(
            sku='SKU-DAAWAT-001',
            barcode='890123400001',
            name='Daawat Rozana Super Basmati Rice 5kg',
            category_id=category.id,
            cost_price=320.00,
            price=449.00,
            mrp=550.00,
            unit='kg',
            is_available=True
        )
        prod2 = Product(
            sku='SKU-FORTUNE-002',
            barcode='890123400002',
            name='Fortune Sunlite Refined Sunflower Oil 1L',
            category_id=category.id,
            cost_price=110.00,
            price=145.00,
            mrp=175.00,
            unit='litre',
            is_available=True
        )
        db.session.add_all([prod1, prod2])
        db.session.flush()

        inv1 = Inventory(
            product_id=prod1.id,
            store_id=store.id,
            stock_quantity=100,
            safety_stock_level=20,
            reorder_quantity=50
        )
        inv2 = Inventory(
            product_id=prod2.id,
            store_id=store.id,
            stock_quantity=150,
            safety_stock_level=30,
            reorder_quantity=60
        )
        db.session.add_all([inv1, inv2])

        # 6. Sample Coupon
        coupon = Coupon(
            code='SAVE10',
            discount_percent=10.0,
            min_order_amount=200.0,
            max_discount_amount=50.0,
            usage_limit=500,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            is_active=True
        )
        db.session.add(coupon)
        db.session.commit()

        # Capture IDs to avoid DetachedInstanceError across sessions
        data = {
            'admin_id': admin_user.id,
            'emp_id': emp_user.id,
            'cust_id': cust_user.id,
            'customer_id': customer.id,
            'store_id': store.id,
            'category_id': category.id,
            'prod1_id': prod1.id,
            'prod2_id': prod2.id,
            'prod1_sku': prod1.sku,
            'prod1_barcode': prod1.barcode,
            'prod2_sku': prod2.sku,
            'prod2_barcode': prod2.barcode,
            'coupon_id': coupon.id,
            'coupon_code': coupon.code
        }
        return data


@pytest.fixture
def admin_headers(app, sample_data):
    """Auth header with valid Admin JWT token."""
    with app.app_context():
        token = create_access_token(
            identity=str(sample_data['admin_id']),
            additional_claims={'role': 'ADMIN', 'username': 'test_admin'}
        )
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


@pytest.fixture
def employee_headers(app, sample_data):
    """Auth header with valid Employee JWT token."""
    with app.app_context():
        token = create_access_token(
            identity=str(sample_data['emp_id']),
            additional_claims={'role': 'EMPLOYEE', 'username': 'test_cashier'}
        )
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


@pytest.fixture
def customer_headers(app, sample_data):
    """Auth header with valid Customer JWT token."""
    with app.app_context():
        token = create_access_token(
            identity=str(sample_data['cust_id']),
            additional_claims={'role': 'CUSTOMER', 'username': 'test_customer'}
        )
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
