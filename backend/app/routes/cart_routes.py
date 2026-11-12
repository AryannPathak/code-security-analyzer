"""Online Customer Shopping Cart routes for SmartFlow."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.app.extensions import db
from backend.app.models.cart import Cart, CartItem
from backend.app.models.catalog import Product
from backend.app.auth.decorators import get_current_user

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


def get_or_create_customer_cart(user):
    """Retrieve or create customer cart."""
    if not user.customer_profile:
        return None
    cart = Cart.query.filter_by(customer_id=user.customer_profile.id).first()
    if not cart:
        cart = Cart(customer_id=user.customer_profile.id)
        db.session.add(cart)
        db.session.commit()
    return cart


@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    """Fetch active shopping cart for authenticated customer."""
    user = get_current_user()
    if not user or not user.customer_profile:
        return jsonify({'success': False, 'error': 'Customer account required'}), 403

    cart = get_or_create_customer_cart(user)
    return jsonify({'success': True, 'cart': cart.to_dict()}), 200


@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add a product to customer's shopping cart."""
    user = get_current_user()
    if not user or not user.customer_profile:
        return jsonify({'success': False, 'error': 'Customer account required'}), 403

    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if not product_id or quantity <= 0:
        return jsonify({'success': False, 'error': 'Valid product_id and positive quantity required'}), 400

    product = Product.query.get(product_id)
    if not product or not product.is_available:
        return jsonify({'success': False, 'error': 'Product is not available for purchase'}), 404

    cart = get_or_create_customer_cart(user)
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Item added to cart', 'cart': cart.to_dict()}), 200


@cart_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_cart_item():
    """Update item quantity in cart."""
    user = get_current_user()
    if not user or not user.customer_profile:
        return jsonify({'success': False, 'error': 'Customer account required'}), 403

    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 0))

    cart = get_or_create_customer_cart(user)
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    if not item:
        return jsonify({'success': False, 'error': 'Item not in cart'}), 404

    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity

    db.session.commit()
    return jsonify({'success': True, 'message': 'Cart updated', 'cart': cart.to_dict()}), 200


@cart_bp.route('/remove/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_cart_item(product_id):
    """Remove a product from cart."""
    user = get_current_user()
    if not user or not user.customer_profile:
        return jsonify({'success': False, 'error': 'Customer account required'}), 403

    cart = get_or_create_customer_cart(user)
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    if item:
        db.session.delete(item)
        db.session.commit()

    return jsonify({'success': True, 'message': 'Item removed from cart', 'cart': cart.to_dict()}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from customer cart."""
    user = get_current_user()
    if not user or not user.customer_profile:
        return jsonify({'success': False, 'error': 'Customer account required'}), 403

    cart = get_or_create_customer_cart(user)
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()

    return jsonify({'success': True, 'message': 'Cart emptied', 'cart': cart.to_dict()}), 200
