"""DMart-style Point-of-Sale (POS) Retail Billing routes for SmartFlow."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.app.extensions import db
from backend.app.models.user import Customer, User
from backend.app.models.order import Transaction, Order
from backend.app.models.store_inventory import Store
from backend.app.services.checkout_service import process_checkout
from backend.app.auth.decorators import get_current_user, employee_required

pos_bp = Blueprint('pos', __name__, url_prefix='/api/pos')


@pos_bp.route('/checkout', methods=['POST'])
@employee_required()
def pos_checkout():
    """Execute DMart POS fast checkout and generate printed customer receipt."""
    user = get_current_user()
    data = request.get_json() or {}

    store_id = data.get('store_id')
    if not store_id and user.employee_profile:
        store_id = user.employee_profile.store_id
    if not store_id:
        store_id = 2  # Default to DMart Store 1 (Andheri)

    items = data.get('items', [])
    payment_method = data.get('payment_method', 'CASH').upper()
    customer_phone = data.get('customer_phone', '').strip()
    customer_name = data.get('customer_name', '').strip() or 'Store Customer'
    coupon_code = data.get('coupon_code')
    idempotency_key = data.get('idempotency_key')

    if not items:
        return jsonify({'success': False, 'error': 'POS billing cart cannot be empty'}), 400

    # Optional: Attach or auto-register loyalty customer by phone
    customer_id = None
    if customer_phone:
        customer = Customer.query.filter_by(phone=customer_phone).first()
        if not customer:
            # Create a loyalty profile
            username = f"loyalty_{customer_phone[-4:]}_{customer_phone[:4]}"
            demo_user = User(
                username=username,
                email=f"{username}@smartflow-pos.local",
                role='CUSTOMER',
                is_active=True
            )
            demo_user.set_password('Loyalty@123')
            db.session.add(demo_user)
            db.session.flush()

            customer = Customer(
                user_id=demo_user.id,
                full_name=customer_name,
                phone=customer_phone,
                city='Local Retail'
            )
            db.session.add(customer)
            db.session.flush()
        customer_id = customer.id

    employee_id = user.employee_profile.id if user and user.employee_profile else None

    success, result = process_checkout(
        order_type='STORE',
        store_id=store_id,
        items=items,
        payment_method=payment_method,
        customer_id=customer_id,
        employee_id=employee_id,
        coupon_code=coupon_code,
        idempotency_key=idempotency_key
    )

    if not success:
        return jsonify({'success': False, 'error': result.get('error')}), 400

    return jsonify({
        'success': True,
        'message': 'Bill generated and stock deducted successfully.',
        'data': result
    }), 201


@pos_bp.route('/transactions', methods=['GET'])
@employee_required()
def get_pos_transactions():
    """Retrieve POS transactions for current cashier terminal / store."""
    user = get_current_user()
    store_id = request.args.get('store_id', type=int)
    if not store_id and user.employee_profile:
        store_id = user.employee_profile.store_id

    query = Transaction.query.filter(Transaction.source == 'STORE')
    if store_id:
        query = query.filter(Transaction.store_id == store_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'total': pagination.total,
        'pages': pagination.pages,
        'transactions': [t.to_dict() for t in pagination.items]
    }), 200
