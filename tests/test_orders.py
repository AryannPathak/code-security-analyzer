"""Online Order Lifecycle, Idempotency & Cancellation Test Suite."""
import uuid
import pytest
from backend.app.models.store_inventory import Inventory
from backend.app.models.order import Order, Transaction


def test_online_order_placement_success(app, client, sample_data, customer_headers):
    """Test customer placing an online order (Amazon-style checkout)."""
    store_id = sample_data['store_id']
    prod1_id = sample_data['prod1_id']

    with app.app_context():
        inv_before = Inventory.query.filter_by(store_id=store_id, product_id=prod1_id).first()
        initial_stock = inv_before.stock_quantity

    payload = {
        'store_id': store_id,
        'payment_method': 'CARD',
        'shipping_address': 'Flat 402, Sunshine Heights, Mumbai',
        'items': [
            {'product_id': prod1_id, 'quantity': 3}
        ]
    }

    response = client.post('/api/orders', json=payload, headers=customer_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data
    order = data['data']['order']
    assert order['order_type'] == 'ONLINE'
    assert order['order_status'] == 'CONFIRMED'

    # Check inventory deduction
    with app.app_context():
        inv_after = Inventory.query.filter_by(store_id=store_id, product_id=prod1_id).first()
        assert inv_after.stock_quantity == initial_stock - 3


def test_idempotency_key_prevents_duplicate_charge(app, client, sample_data, customer_headers):
    """Test submitting identical request with the same idempotency_key returns cached response without duplicate stock deduction."""
    store_id = sample_data['store_id']
    prod2_id = sample_data['prod2_id']
    idem_key = f"IDEM-TEST-{uuid.uuid4().hex}"

    with app.app_context():
        inv_start = Inventory.query.filter_by(store_id=store_id, product_id=prod2_id).first()
        start_stock = inv_start.stock_quantity

    payload = {
        'store_id': store_id,
        'payment_method': 'UPI',
        'idempotency_key': idem_key,
        'items': [
            {'product_id': prod2_id, 'quantity': 5}
        ]
    }

    # Request 1
    res1 = client.post('/api/orders', json=payload, headers=customer_headers)
    assert res1.status_code == 201
    data1 = res1.get_json()
    order_num1 = data1['data']['order']['order_number']

    # Request 2 (Duplicate replay)
    res2 = client.post('/api/orders', json=payload, headers=customer_headers)
    assert res2.status_code in (200, 201)
    data2 = res2.get_json()
    assert data2['data']['order']['order_number'] == order_num1

    # Verify inventory stock was decremented ONLY ONCE (by 5, not 10)
    with app.app_context():
        inv_end = Inventory.query.filter_by(store_id=store_id, product_id=prod2_id).first()
        assert inv_end.stock_quantity == start_stock - 5


def test_customer_view_orders(client, sample_data, customer_headers):
    """Test customer listing their own orders."""
    response = client.get('/api/orders', headers=customer_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'orders' in data
    assert 'total' in data


def test_cancel_order_restores_inventory(app, client, sample_data, customer_headers):
    """Test cancelling an order restores product stock to inventory."""
    store_id = sample_data['store_id']
    prod1_id = sample_data['prod1_id']

    # Place order
    payload = {
        'store_id': store_id,
        'payment_method': 'CARD',
        'items': [{'product_id': prod1_id, 'quantity': 4}]
    }
    place_res = client.post('/api/orders', json=payload, headers=customer_headers)
    assert place_res.status_code == 201
    order_data = place_res.get_json()['data']['order']
    order_id = order_data['id']

    with app.app_context():
        inv_mid = Inventory.query.filter_by(store_id=store_id, product_id=prod1_id).first()
        stock_after_order = inv_mid.stock_quantity

    # Cancel order
    cancel_res = client.put(f'/api/orders/{order_id}/cancel', headers=customer_headers)
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.get_json()
    assert cancel_data['success'] is True
    assert cancel_data['order']['order_status'] == 'CANCELLED'

    # Verify stock restored
    with app.app_context():
        inv_restored = Inventory.query.filter_by(store_id=store_id, product_id=prod1_id).first()
        assert inv_restored.stock_quantity == stock_after_order + 4


def test_employee_update_order_status(client, sample_data, customer_headers, employee_headers):
    """Test staff updating order fulfillment status."""
    # Place an order first
    payload = {
        'store_id': sample_data['store_id'],
        'payment_method': 'CARD',
        'items': [{'product_id': sample_data['prod1_id'], 'quantity': 1}]
    }
    place_res = client.post('/api/orders', json=payload, headers=customer_headers)
    order_id = place_res.get_json()['data']['order']['id']

    # Update status to SHIPPED
    status_res = client.put(f'/api/orders/{order_id}/status', json={'status': 'SHIPPED'}, headers=employee_headers)
    assert status_res.status_code == 200
    assert status_res.get_json()['order']['order_status'] == 'SHIPPED'
