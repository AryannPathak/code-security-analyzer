"""Inventory management and stock audit routes for SmartFlow."""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from backend.app.extensions import db
from backend.app.models.store_inventory import Inventory, Store, StockHistory
from backend.app.models.catalog import Product
from backend.app.auth.decorators import employee_required, admin_required

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')


@inventory_bp.route('', methods=['GET'])
def get_inventory():
    """List inventory items across stores with filtering and search."""
    query = Inventory.query.join(Product).join(Store)

    store_id = request.args.get('store_id', type=int)
    if store_id:
        query = query.filter(Inventory.store_id == store_id)

    low_stock_only = request.args.get('low_stock', 'false').lower() == 'true'
    if low_stock_only:
        query = query.filter(Inventory.stock_quantity <= Inventory.safety_stock_level)

    search = request.args.get('search', '').strip()
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_filter)) |
            (Product.sku.ilike(search_filter)) |
            (Product.barcode.ilike(search_filter)) |
            (Store.name.ilike(search_filter))
        )

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    pagination = query.order_by(Inventory.stock_quantity.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'inventory': [item.to_dict() for item in pagination.items]
    }), 200


@inventory_bp.route('/low-stock', methods=['GET'])
def get_low_stock_alerts():
    """Retrieve all store items operating below their safety threshold."""
    store_id = request.args.get('store_id', type=int)
    query = Inventory.query.filter(Inventory.stock_quantity <= Inventory.safety_stock_level)
    if store_id:
        query = query.filter(Inventory.store_id == store_id)

    low_stock_items = query.order_by(Inventory.stock_quantity.asc()).all()
    return jsonify({
        'success': True,
        'count': len(low_stock_items),
        'items': [item.to_dict() for item in low_stock_items]
    }), 200


@inventory_bp.route('/restock', methods=['POST'])
@employee_required()
def restock_inventory():
    """Add incoming stock shipment to a store inventory record."""
    data = request.get_json() or {}
    store_id = data.get('store_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    reference_id = data.get('reference_id', 'SHIPMENT-IN')
    notes = data.get('notes', 'Warehouse batch restock')

    if not store_id or not product_id or not quantity or int(quantity) <= 0:
        return jsonify({'success': False, 'error': 'store_id, product_id, and positive quantity required'}), 400

    inv = Inventory.query.filter_by(store_id=store_id, product_id=product_id).first()
    if not inv:
        inv = Inventory(
            store_id=store_id,
            product_id=product_id,
            stock_quantity=0,
            safety_stock_level=15,
            reorder_quantity=60
        )
        db.session.add(inv)
        db.session.flush()

    inv.stock_quantity += int(quantity)
    inv.last_restocked_at = datetime.now(timezone.utc)

    # Immutable stock history audit
    history = StockHistory(
        product_id=product_id,
        store_id=store_id,
        change_type='RESTOCK',
        quantity_changed=int(quantity),
        balance_after=inv.stock_quantity,
        reference_id=reference_id,
        notes=notes
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Restocked {quantity} units successfully',
        'inventory': inv.to_dict()
    }), 200


@inventory_bp.route('/history', methods=['GET'])
@employee_required()
def get_stock_history():
    """Retrieve audit history trail of stock changes."""
    query = StockHistory.query
    product_id = request.args.get('product_id', type=int)
    store_id = request.args.get('store_id', type=int)

    if product_id:
        query = query.filter(StockHistory.product_id == product_id)
    if store_id:
        query = query.filter(StockHistory.store_id == store_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    pagination = query.order_by(StockHistory.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'total': pagination.total,
        'pages': pagination.pages,
        'history': [h.to_dict() for h in pagination.items]
    }), 200
