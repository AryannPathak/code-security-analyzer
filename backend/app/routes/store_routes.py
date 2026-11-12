"""Physical Store and Warehouse management routes for SmartFlow."""
from flask import Blueprint, request, jsonify
from backend.app.extensions import db
from backend.app.models.store_inventory import Store
from backend.app.auth.decorators import admin_required

store_bp = Blueprint('stores', __name__, url_prefix='/api/stores')


@store_bp.route('', methods=['GET'])
def get_stores():
    """List all physical stores and hubs."""
    stores = Store.query.order_by(Store.id.asc()).all()
    return jsonify({
        'success': True,
        'count': len(stores),
        'stores': [s.to_dict() for s in stores]
    }), 200


@store_bp.route('/<int:store_id>', methods=['GET'])
def get_store(store_id):
    """Retrieve details for a single store branch."""
    store = Store.query.get_or_404(store_id)
    return jsonify({'success': True, 'store': store.to_dict()}), 200


@store_bp.route('', methods=['POST'])
@admin_required()
def create_store():
    """Register a new physical store or warehouse branch (Admin only)."""
    data = request.get_json() or {}
    store_code = data.get('store_code', '').strip().upper()
    name = data.get('name', '').strip()
    location = data.get('location', '').strip()
    city = data.get('city', '').strip()
    phone = data.get('phone', '').strip()

    if not store_code or not name or not location or not city:
        return jsonify({'success': False, 'error': 'store_code, name, location, and city are required'}), 400

    if Store.query.filter_by(store_code=store_code).first():
        return jsonify({'success': False, 'error': f'Store code {store_code} already exists'}), 409

    store = Store(
        store_code=store_code,
        name=name,
        location=location,
        city=city,
        phone=phone,
        is_active=True
    )
    db.session.add(store)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Store created successfully', 'store': store.to_dict()}), 201


@store_bp.route('/<int:store_id>', methods=['PUT'])
@admin_required()
def update_store(store_id):
    """Update store details (Admin only)."""
    store = Store.query.get_or_404(store_id)
    data = request.get_json() or {}

    if 'name' in data:
        store.name = data['name'].strip()
    if 'location' in data:
        store.location = data['location'].strip()
    if 'city' in data:
        store.city = data['city'].strip()
    if 'phone' in data:
        store.phone = data['phone'].strip()
    if 'is_active' in data:
        store.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({'success': True, 'message': 'Store updated', 'store': store.to_dict()}), 200
