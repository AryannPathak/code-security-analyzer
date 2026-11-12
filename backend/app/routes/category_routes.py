"""Category management routes for SmartFlow."""
from flask import Blueprint, request, jsonify
from backend.app.extensions import db
from backend.app.models.catalog import Category
from backend.app.auth.decorators import admin_required

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


@category_bp.route('', methods=['GET'])
def get_categories():
    """List all categories with product counts."""
    categories = Category.query.order_by(Category.name.asc()).all()
    return jsonify({
        'success': True,
        'count': len(categories),
        'categories': [c.to_dict() for c in categories]
    }), 200


@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Retrieve single category."""
    category = Category.query.get_or_404(category_id)
    return jsonify({'success': True, 'category': category.to_dict()}), 200


@category_bp.route('', methods=['POST'])
@admin_required()
def create_category():
    """Create a new category (Admin only)."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    image_url = data.get('image_url', '').strip()

    if not name:
        return jsonify({'success': False, 'error': 'Category name is required'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'success': False, 'error': 'Category name already exists'}), 409

    category = Category(name=name, description=description, image_url=image_url)
    db.session.add(category)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Category created successfully', 'category': category.to_dict()}), 201


@category_bp.route('/<int:category_id>', methods=['PUT'])
@admin_required()
def update_category(category_id):
    """Update existing category (Admin only)."""
    category = Category.query.get_or_404(category_id)
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    if name and name != category.name:
        if Category.query.filter_by(name=name).first():
            return jsonify({'success': False, 'error': 'Category name already exists'}), 409
        category.name = name

    if 'description' in data:
        category.description = data['description']
    if 'image_url' in data:
        category.image_url = data['image_url']
    if 'is_active' in data:
        category.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({'success': True, 'message': 'Category updated', 'category': category.to_dict()}), 200


@category_bp.route('/<int:category_id>', methods=['DELETE'])
@admin_required()
def delete_category(category_id):
    """Delete category if no products linked (Admin only)."""
    category = Category.query.get_or_404(category_id)
    if category.products.count() > 0:
        return jsonify({
            'success': False,
            'error': f'Cannot delete category with {category.products.count()} associated products.'
        }), 400

    db.session.delete(category)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Category deleted successfully'}), 200
