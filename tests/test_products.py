"""Product Catalog & Barcode Scanner Test Suite."""
import pytest


def test_get_product_catalog(client, sample_data):
    """Test public listing of catalog products."""
    response = client.get('/api/products')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'products' in data
    assert len(data['products']) >= 2
    assert 'current_page' in data
    assert 'total' in data


def test_get_product_catalog_filter_by_search(client, sample_data):
    """Test searching products by keyword query."""
    response = client.get('/api/products?search=Basmati')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert any('Basmati' in p['name'] for p in data['products'])


def test_get_product_by_barcode(client, sample_data):
    """Test scanning a barcode at POS cashier terminal."""
    barcode = sample_data['prod1_barcode']
    response = client.get(f'/api/products/barcode/{barcode}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['product']['barcode'] == barcode
    assert data['product']['id'] == sample_data['prod1_id']


def test_get_product_by_sku(client, sample_data):
    """Test looking up a product by SKU."""
    sku = sample_data['prod2_sku']
    response = client.get(f'/api/products/barcode/{sku}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['product']['sku'] == sku


def test_get_nonexistent_barcode_returns_404(client, sample_data):
    """Test barcode scan of invalid code returns 404."""
    response = client.get('/api/products/barcode/999999999999')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False


def test_admin_create_product_success(client, sample_data, admin_headers):
    """Test admin adding a new product to master catalog."""
    payload = {
        'category_id': sample_data['category_id'],
        'name': 'Tata Tea Gold 500g',
        'brand': 'Tata',
        'unit': 'pack',
        'cost_price': 180.0,
        'price': 240.0,
        'mrp': 275.0,
        'initial_stock': 80
    }
    response = client.post('/api/products', json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['product']['name'] == 'Tata Tea Gold 500g'
    assert 'sku' in data['product']
    assert 'barcode' in data['product']


def test_customer_cannot_create_product(client, sample_data, customer_headers):
    """Verify customer cannot create products (RBAC enforcement)."""
    payload = {
        'category_id': sample_data['category_id'],
        'name': 'Unauthorized Product',
        'price': 100.0
    }
    response = client.post('/api/products', json=payload, headers=customer_headers)
    assert response.status_code == 403


def test_admin_update_product(client, sample_data, admin_headers):
    """Test updating product price and details."""
    prod_id = sample_data['prod1_id']
    payload = {
        'price': 429.00,
        'name': 'Daawat Rozana Super Basmati Rice 5kg (Special Offer)'
    }
    response = client.put(f'/api/products/{prod_id}', json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['product']['price'] == 429.00
    assert 'Special Offer' in data['product']['name']
