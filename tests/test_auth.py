"""Authentication & Authorization Test Suite."""
import pytest


def test_customer_registration_success(client):
    """Test creating a new customer account."""
    payload = {
        'username': 'new_shopper',
        'email': 'shopper@testsmartflow.com',
        'password': 'SecurePassword@123',
        'full_name': 'Aarav Mehta',
        'phone': '9123456789',
        'address': 'Flat 402, Sunshine Heights',
        'city': 'Mumbai'
    }
    response = client.post('/api/auth/register', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert 'token' in data
    assert data['user']['username'] == 'new_shopper'
    assert data['user']['role'] == 'CUSTOMER'


def test_customer_registration_duplicate_username_fails(client, sample_data):
    """Test duplicate registration returns 409 conflict."""
    payload = {
        'username': 'test_customer',  # already exists in sample_data
        'email': 'unique_email@test.com',
        'password': 'Password@123',
        'full_name': 'Duplicate User'
    }
    response = client.post('/api/auth/register', json=payload)
    assert response.status_code == 409
    data = response.get_json()
    assert data['success'] is False


def test_login_successful(client, sample_data):
    """Test authenticating with valid credentials returns JWT token."""
    response = client.post('/api/auth/login', json={
        'username': 'test_admin',
        'password': 'Admin@12345'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'token' in data
    assert data['user']['role'] == 'ADMIN'


def test_login_invalid_password_fails(client, sample_data):
    """Test authenticating with wrong password returns 401 Unauthorized."""
    response = client.post('/api/auth/login', json={
        'username': 'test_admin',
        'password': 'WrongPassword@999'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False


def test_get_user_profile_authenticated(client, sample_data, admin_headers):
    """Test fetching profile using valid Bearer JWT token."""
    response = client.get('/api/auth/profile', headers=admin_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['user']['username'] == 'test_admin'
    assert data['user']['role'] == 'ADMIN'


def test_demo_credentials_endpoint(client):
    """Test that demo credentials endpoint returns the 3 role presets."""
    response = client.get('/api/auth/demo-credentials')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    roles = [acc['role'] for acc in data['accounts']]
    assert 'ADMIN' in roles
    assert 'EMPLOYEE' in roles
    assert 'CUSTOMER' in roles
