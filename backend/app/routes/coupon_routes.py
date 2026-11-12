"""Discount Coupon and Promotional code routes for SmartFlow."""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from backend.app.extensions import db
from backend.app.models.cart import Coupon
from backend.app.auth.decorators import admin_required

coupon_bp = Blueprint('coupons', __name__, url_prefix='/api/coupons')


@coupon_bp.route('', methods=['GET'])
def get_coupons():
    """List active coupons (or all coupons for admin)."""
    coupons = Coupon.query.order_by(Coupon.id.desc()).all()
    return jsonify({
        'success': True,
        'count': len(coupons),
        'coupons': [c.to_dict() for c in coupons]
    }), 200


@coupon_bp.route('/validate', methods=['POST'])
def validate_coupon():
    """Validate a coupon against an order amount and return discount."""
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    order_amount = float(data.get('order_amount', 0.0))

    if not code:
        return jsonify({'success': False, 'error': 'Coupon code is required'}), 400

    coupon = Coupon.query.filter_by(code=code).first()
    if not coupon:
        return jsonify({'success': False, 'error': f'Coupon "{code}" is invalid or does not exist'}), 404

    is_valid, msg = coupon.is_valid(order_amount)
    if not is_valid:
        return jsonify({'success': False, 'error': msg}), 400

    discount = coupon.calculate_discount(order_amount)
    payable = max(order_amount - discount, 0.0)

    return jsonify({
        'success': True,
        'message': f'Coupon applied! You saved ₹{discount:.2f}',
        'coupon': {
            'code': coupon.code,
            'discount_percent': float(coupon.discount_percent),
            'discount_amount': discount,
            'original_amount': order_amount,
            'final_amount': round(payable, 2)
        }
    }), 200


@coupon_bp.route('', methods=['POST'])
@admin_required()
def create_coupon():
    """Create a new promotional coupon (Admin only)."""
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    discount_percent = data.get('discount_percent')
    expires_at_str = data.get('expires_at')

    if not code or discount_percent is None or not expires_at_str:
        return jsonify({'success': False, 'error': 'code, discount_percent, and expires_at required'}), 400

    if Coupon.query.filter_by(code=code).first():
        return jsonify({'success': False, 'error': 'Coupon code already exists'}), 409

    try:
        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid ISO date for expires_at (e.g. 2026-12-31T23:59:59)'}), 400

    coupon = Coupon(
        code=code,
        discount_percent=float(discount_percent),
        max_discount_amount=float(data['max_discount_amount']) if data.get('max_discount_amount') else None,
        min_order_amount=float(data.get('min_order_amount', 0.0)),
        usage_limit=int(data.get('usage_limit', 1000)),
        expires_at=expires_at,
        is_active=bool(data.get('is_active', True))
    )
    db.session.add(coupon)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Coupon created', 'coupon': coupon.to_dict()}), 201


@coupon_bp.route('/<int:coupon_id>', methods=['DELETE'])
@admin_required()
def delete_coupon(coupon_id):
    """Delete a coupon (Admin only)."""
    coupon = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Coupon deleted'}), 200
