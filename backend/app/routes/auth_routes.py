"""Authentication API routes for SmartFlow."""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.app.extensions import db
from backend.app.models.user import User, Customer, Employee
from backend.app.models.cart import Cart
from backend.app.models.analytics_ai import AuditLog
from backend.app.auth.decorators import get_current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new customer account."""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()
    city = data.get('city', '').strip()

    if not username or not email or not password or not full_name:
        return jsonify({
            'success': False,
            'error': 'Missing required fields (username, email, password, full_name)'
        }), 400

    if len(password) < 6:
        return jsonify({
            'success': False,
            'error': 'Password must be at least 6 characters long'
        }), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({
            'success': False,
            'error': 'Username or Email is already registered'
        }), 409

    try:
        user = User(
            username=username,
            email=email,
            role='CUSTOMER',
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        customer = Customer(
            user_id=user.id,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city
        )
        db.session.add(customer)
        db.session.flush()

        # Initialize empty cart for customer
        cart = Cart(customer_id=customer.id)
        db.session.add(cart)

        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action='USER_REGISTER',
            entity_type='USER',
            entity_id=str(user.id),
            details=f"New customer registered: {username} ({email})"
        )
        db.session.add(audit)
        db.session.commit()

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'username': user.username}
        )

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT access token."""
    data = request.get_json() or {}
    identifier = data.get('username', '').strip()
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'success': False, 'error': 'Username/Email and Password are required'}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid username/email or password'}), 401

    if not user.is_active:
        return jsonify({'success': False, 'error': 'Account is suspended or deactivated'}), 403

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )

    return jsonify({
        'success': True,
        'message': f'Welcome back, {user.username}!',
        'token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Fetch profile of currently authenticated user."""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    return jsonify({'success': True, 'user': user.to_dict()}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Simulated JWT logout."""
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@auth_bp.route('/demo-credentials', methods=['GET'])
def get_demo_credentials():
    """Return preconfigured demo accounts for quick evaluation."""
    return jsonify({
        'success': True,
        'accounts': [
            {'role': 'ADMIN', 'username': 'admin', 'password': 'Admin@12345', 'description': 'Full Master Administrator'},
            {'role': 'EMPLOYEE', 'username': 'cashier_mumbai', 'password': 'Cashier@12345', 'description': 'DMart Store Cashier (Andheri Branch)'},
            {'role': 'CUSTOMER', 'username': 'customer_demo', 'password': 'Customer@12345', 'description': 'Amazon E-Commerce Shopper'}
        ]
    }), 200
