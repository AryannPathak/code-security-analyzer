"""DMart POS Retail Checkout & Receipt Verification Test Suite."""
import pytest
from backend.app.models.store_inventory import Inventory
from backend.app.models.order import Order, Transaction


def test_pos_checkout_cash_success(app, client, sample_data, employee_headers):
    """Test standard POS cash checkout at physical store cashier."""
    store_id = sample_data['store_id']
    prod1_id = sample_data['prod1_id']

    # Initial stock before checkout
    with app.app_context():
        inv_before = Inventory.query.filter_by(store_id=store_id, product_id=prod1_id).first()
        initial_stock = inv_before.stock_quantity

    payload = {
        'store_id': store_id,
        'payment_method': 'CASH',
        'customer_name': 'Walk-in Shopper',
        'items': [
            {'product_id': prod1_id, 'quantity': 2}
        ]
    }

    response = client.post('/api/pos/checkout', json=payload, headers=employee_headers)
    assert response.status_code == 201, f"Response: {response.get_json()}"
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data
    assert 'receipt' in data['data']

    receipt = data['data']['receipt']
    assert receipt['store_name'] == 'DMart Flagship Mumbai'
    assert receipt['payment_method'] == 'CASH'
    order = data['data']['order']
    assert order['order_type'] == 'STORE'
    assert len(order['items']) == 1
    assert order['items'][0]['quantity'] == 2

    # Verify inventory stock was decremented by 2
    with app.app_context():
        inv_after = Inventory.query.filter_by(store_id=store_id, product_id=prod1_id).first()
        assert inv_after.stock_quantity == initial_stock - 2

        # Verify Centralized Transaction record was created
        txn = Transaction.query.filter_by(order_id=data['data']['order']['id']).first()
        assert txn is not None
        assert txn.source == 'STORE'
        assert txn.status == 'SUCCESS'


def test_pos_checkout_with_coupon(client, sample_data, employee_headers):
    """Test applying coupon discount during POS billing."""
    store_id = sample_data['store_id']
    prod1_id = sample_data['prod1_id']

    payload = {
        'store_id': store_id,
        'payment_method': 'UPI',
        'coupon_code': 'SAVE10',
        'items': [
            {'product_id': prod1_id, 'quantity': 1}  # Price is 449.00
        ]
    }

    response = client.post('/api/pos/checkout', json=payload, headers=employee_headers)
    assert response.status_code == 201, f"Response: {response.get_json()}"
    data = response.get_json()
    assert data['success'] is True
    receipt = data['data']['receipt']
    assert receipt['discount'] > 0


def test_pos_checkout_insufficient_stock_fails(client, sample_data, employee_headers):
    """Test attempting to sell more items than in store inventory fails."""
    store_id = sample_data['store_id']
    prod1_id = sample_data['prod1_id']

    payload = {
        'store_id': store_id,
        'payment_method': 'CASH',
        'items': [
            {'product_id': prod1_id, 'quantity': 9999}  # Far exceeds stock
        ]
    }

    response = client.post('/api/pos/checkout', json=payload, headers=employee_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'stock' in data['error'].lower()


def test_pos_checkout_empty_items_fails(client, sample_data, employee_headers):
    """Test submitting empty billing cart returns 400."""
    payload = {
        'store_id': sample_data['store_id'],
        'payment_method': 'CASH',
        'items': []
    }
    response = client.post('/api/pos/checkout', json=payload, headers=employee_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_get_pos_transactions(client, sample_data, employee_headers):
    """Test cashier listing store transactions."""
    response = client.get('/api/pos/transactions', headers=employee_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'transactions' in data
