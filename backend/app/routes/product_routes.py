"""Product management and catalog search routes for SmartFlow."""
import random
import string
from flask import Blueprint, request, jsonify
from backend.app.extensions import db
from backend.app.models.catalog import Product, Category
from backend.app.models.store_inventory import Inventory, Store, StockHistory
from backend.app.auth.decorators import admin_required

product_bp = Blueprint('products', __name__, url_prefix='/api/products')


def generate_unique_sku(category_name: str = 'GEN') -> str:
    """Generate a clean enterprise SKU code, e.g., GRO-9482-A7."""
    prefix = ''.join([c for c in category_name.upper() if c.isalnum()][:3]) or 'PRD'
    num = random.randint(1000, 9999)
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
    sku = f"{prefix}-{num}-{suffix}"
    while Product.query.filter_by(sku=sku).first():
        num = random.randint(1000, 9999)
        sku = f"{prefix}-{num}-{suffix}"
    return sku


def generate_unique_barcode() -> str:
    """Generate a standard 12-digit UPC/EAN style numeric barcode."""
    code = "890" + "".join([str(random.randint(0, 9)) for _ in range(9)])
    while Product.query.filter_by(barcode=code).first():
        code = "890" + "".join([str(random.randint(0, 9)) for _ in range(9)])
    return code


@product_bp.route('', methods=['GET'])
def get_products():
    """Retrieve catalog products with full search, filtering, sorting and pagination."""
    query = Product.query

    # Search by keyword (name, description, brand, SKU, or barcode)
    search = request.args.get('search', '').strip()
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_filter)) |
            (Product.brand.ilike(search_filter)) |
            (Product.sku.ilike(search_filter)) |
            (Product.barcode.ilike(search_filter)) |
            (Product.description.ilike(search_filter))
        )

    # Category filter
    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Brand filter
    brand = request.args.get('brand', '').strip()
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))

    # Price range
    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Availability filter
    if request.args.get('available_only', 'false').lower() == 'true':
        query = query.filter(Product.is_available == True)

    # Sorting
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(Product.name.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(Product.name.desc())
    else:  # newest
        query = query.order_by(Product.id.desc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(max(per_page, 1), 100)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': per_page,
        'products': [p.to_dict(include_inventory=False) for p in pagination.items]
    }), 200


@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Retrieve single product details with full store inventory breakdown."""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'success': True,
        'product': product.to_dict(include_inventory=True)
    }), 200


@product_bp.route('/barcode/<string:barcode>', methods=['GET'])
def get_product_by_barcode(barcode):
    """Fast barcode / SKU lookup for DMart POS cashier terminal."""
    clean_code = barcode.strip()
    product = Product.query.filter(
        (Product.barcode == clean_code) | (Product.sku == clean_code)
    ).first()

    if not product:
        return jsonify({'success': False, 'error': f'Product with barcode/SKU "{clean_code}" not found'}), 404

    return jsonify({
        'success': True,
        'product': product.to_dict(include_inventory=True)
    }), 200


@product_bp.route('', methods=['POST'])
@admin_required()
def create_product():
    """Create a new product in master catalog (Admin only)."""
    data = request.get_json() or {}

    category_id = data.get('category_id')
    name = data.get('name', '').strip()
    price = data.get('price')
    mrp = data.get('mrp', price)
    cost_price = data.get('cost_price', float(price) * 0.7 if price else 0)

    if not category_id or not name or price is None:
        return jsonify({'success': False, 'error': 'category_id, name, and price are required'}), 400

    category = Category.query.get(category_id)
    if not category:
        return jsonify({'success': False, 'error': 'Specified category does not exist'}), 404

    sku = data.get('sku', '').strip() or generate_unique_sku(category.name)
    barcode = data.get('barcode', '').strip() or generate_unique_barcode()

    if Product.query.filter((Product.sku == sku) | (Product.barcode == barcode)).first():
        return jsonify({'success': False, 'error': 'SKU or Barcode already exists in system'}), 409

    try:
        product = Product(
            category_id=category_id,
            sku=sku,
            barcode=barcode,
            name=name,
            description=data.get('description', ''),
            brand=data.get('brand', 'SmartFlow Basics'),
            unit=data.get('unit', 'piece'),
            mrp=float(mrp),
            price=float(price),
            cost_price=float(cost_price),
            image_url=data.get('image_url') or 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80',
            is_available=bool(data.get('is_available', True))
        )
        db.session.add(product)
        db.session.flush()

        # Allocate initial inventory across all active stores if initial_stock provided
        initial_stock = int(data.get('initial_stock', 50))
        active_stores = Store.query.filter_by(is_active=True).all()
        for store in active_stores:
            inv = Inventory(
                store_id=store.id,
                product_id=product.id,
                stock_quantity=initial_stock,
                safety_stock_level=int(data.get('safety_stock_level', 15)),
                reorder_quantity=int(data.get('reorder_quantity', 60))
            )
            db.session.add(inv)

            hist = StockHistory(
                product_id=product.id,
                store_id=store.id,
                change_type='RESTOCK',
                quantity_changed=initial_stock,
                balance_after=initial_stock,
                reference_id='INITIAL-CATALOG-ONBOARDING',
                notes='Initial stock on catalog product creation'
            )
            db.session.add(hist)

        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Product created and inventory allocated across stores',
            'product': product.to_dict(include_inventory=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to create product: {str(e)}'}), 500


@product_bp.route('/<int:product_id>', methods=['PUT'])
@admin_required()
def update_product(product_id):
    """Update existing product details (Admin only)."""
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}

    if 'name' in data and data['name'].strip():
        product.name = data['name'].strip()
    if 'category_id' in data:
        product.category_id = int(data['category_id'])
    if 'brand' in data:
        product.brand = data['brand'].strip()
    if 'description' in data:
        product.description = data['description']
    if 'unit' in data:
        product.unit = data['unit']
    if 'mrp' in data:
        product.mrp = float(data['mrp'])
    if 'price' in data:
        product.price = float(data['price'])
    if 'cost_price' in data:
        product.cost_price = float(data['cost_price'])
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'is_available' in data:
        product.is_available = bool(data['is_available'])

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Product updated successfully',
        'product': product.to_dict(include_inventory=True)
    }), 200


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@admin_required()
def delete_product(product_id):
    """Delete or deactivate product from system (Admin only)."""
    product = Product.query.get_or_404(product_id)
    try:
        # If product has historical order items, soft-delete by setting unavailable
        if product.order_items.count() > 0:
            product.is_available = False
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Product marked unavailable to preserve past transaction records.'
            }), 200

        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product permanently deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
