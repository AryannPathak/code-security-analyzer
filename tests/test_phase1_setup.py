"""Phase 1 Architecture, Database & Environment Verification Tests."""
import os
import sys

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


@pytest.fixture
def app():
    """Create application configured for testing."""
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


def test_health_check_endpoint(client):
    """Test that /api/health responds with 200 OK and valid JSON diagnostics."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'database' in data
    assert 'version' in data


def test_all_18_models_instantiation(app):
    """Verify that all 18 database model classes can be queried and have tables."""
    models = [
        User, Customer, Employee, Category, Product, Store, Inventory,
        StockHistory, Order, OrderItem, Transaction, PaymentRecord,
        Cart, CartItem, Coupon, Recommendation, AuditLog
    ]
    with app.app_context():
        for model in models:
            # Query count to ensure table is bound and schema is valid
            count = model.query.count()
            assert isinstance(count, int)


def test_seed_store_and_category_creation(app):
    """Verify relations and constraints on basic entities."""
    with app.app_context():
        store = Store(
            store_code='TEST-01',
            name='Test DMart Branch',
            location='Test Mall',
            city='Mumbai'
        )
        cat = Category(
            name='Test Category',
            description='Test category description'
        )
        db.session.add_all([store, cat])
        db.session.commit()

        assert store.id is not None
        assert cat.id is not None
        assert store.to_dict()['store_code'] == 'TEST-01'
        assert cat.to_dict()['name'] == 'Test Category'
