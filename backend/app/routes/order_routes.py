"""Order management routes for SmartFlow."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.app.extensions import db
from backend.app.models.order import Order, OrderItem, Transaction, Return
from backend.app.models.store_inventory import Inventory, StockHistory
from backend.app.services.checkout_service import process_checkout
from backend.app.auth.decorators import get_current_user, employee_required, admin_required

order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@order_bp.route('', methods=['POST'])
@jwt_required()
def place_order():
    """Place online customer order (Amazon-style checkout)."""
    user = get_current_user()
    if not user or not user.customer_profile:
        return jsonify({'success': False, 'error': 'Customer account required to place online order'}), 403

    data = request.get_json() or {}
    items = data.get('items', [])
    store_id = data.get('store_id', 1)  # Default to central fulfillment hub (id=1)
    payment_method = data.get('payment_method', 'CARD')
    coupon_code = data.get('coupon_code')
    shipping_address = data.get('shipping_address') or user.customer_profile.address or 'Standard Home Delivery'
    idempotency_key = data.get('idempotency_key')

    if not items:
        # If no items explicitly supplied, take items from user's active cart
        cart = user.customer_profile.cart
        if not cart or not cart.items:
            return jsonify({'success': False, 'error': 'Shopping cart is empty'}), 400
        items = [{'product_id': item.product_id, 'quantity': item.quantity} for item in cart.items]

    success, result = process_checkout(
        order_type='ONLINE',
        store_id=store_id,
        items=items,
        payment_method=payment_method,
        customer_id=user.customer_profile.id,
        coupon_code=coupon_code,
        shipping_address=shipping_address,
        idempotency_key=idempotency_key
    )

    if not success:
        return jsonify({'success': False, 'error': result.get('error')}), 400

    return jsonify({
        'success': True,
        'message': 'Order placed successfully',
        'data': result
    }), 201


@order_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """List orders with role-based filtering (Customer views own; Admin/Employee views all)."""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    query = Order.query

    # Customers only see their own orders
    if user.role == 'CUSTOMER':
        if not user.customer_profile:
            return jsonify({'success': True, 'orders': [], 'total': 0}), 200
        query = query.filter(Order.customer_id == user.customer_profile.id)
    else:
        # Admin or Employee filters
        store_id = request.args.get('store_id', type=int)
        if store_id:
            query = query.filter(Order.store_id == store_id)

        order_type = request.args.get('type')  # ONLINE or STORE
        if order_type:
            query = query.filter(Order.order_type == order_type.upper())

        status = request.args.get('status')
        if status:
            query = query.filter(Order.order_status == status.upper())

    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'orders': [o.to_dict(include_items=True) for o in pagination.items]
    }), 200


@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Retrieve detailed order record."""
    user = get_current_user()
    order = Order.query.get_or_404(order_id)

    if user.role == 'CUSTOMER' and order.customer_id != (user.customer_profile.id if user.customer_profile else None):
        return jsonify({'success': False, 'error': 'Unauthorized to view this order'}), 403

    return jsonify({'success': True, 'order': order.to_dict(include_items=True)}), 200


@order_bp.route('/<int:order_id>/status', methods=['PUT'])
@employee_required()
def update_order_status(order_id):
    """Update order fulfillment lifecycle status."""
    order = Order.query.get_or_404(order_id)
    data = request.get_json() or {}
    new_status = data.get('status', '').upper()

    valid_statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'COMPLETED', 'CANCELLED']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'error': f'Invalid status. Allowed: {valid_statuses}'}), 400

    order.order_status = new_status
    db.session.commit()

    return jsonify({'success': True, 'message': f'Order status updated to {new_status}', 'order': order.to_dict()}), 200


@order_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    """Cancel order, restore store inventory and record refund."""
    user = get_current_user()
    order = Order.query.get_or_404(order_id)

    if user.role == 'CUSTOMER' and order.customer_id != (user.customer_profile.id if user.customer_profile else None):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    if order.order_status in ['DELIVERED', 'COMPLETED', 'CANCELLED'] and user.role == 'CUSTOMER':
        return jsonify({
            'success': False,
            'error': f'Order cannot be cancelled in state "{order.order_status}".'
        }), 400

    try:
        # 1. Restore Inventory
        for item in order.items:
            inv = Inventory.query.filter_by(store_id=order.store_id, product_id=item.product_id).first()
            if inv:
                inv.stock_quantity += item.quantity
                stock_hist = StockHistory(
                    product_id=item.product_id,
                    store_id=order.store_id,
                    change_type='RETURN',
                    quantity_changed=item.quantity,
                    balance_after=inv.stock_quantity,
                    reference_id=f"CANCEL-{order.order_number}",
                    notes='Order cancellation stock restoration'
                )
                db.session.add(stock_hist)

            # Record Return
            ret = Return(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                refund_amount=item.subtotal,
                reason='Customer/Admin cancellation',
                status='COMPLETED'
            )
            db.session.add(ret)

        # 2. Update Order and Transactions
        order.order_status = 'CANCELLED'
        for txn in order.transactions:
            txn.status = 'REFUNDED'

        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Order cancelled successfully and inventory balance restored.',
            'order': order.to_dict(include_items=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Cancellation failed: {str(e)}'}), 500
