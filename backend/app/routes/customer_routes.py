"""Customer management routes for SmartFlow."""
from flask import Blueprint, request, jsonify
from backend.app.models.user import Customer, User
from backend.app.auth.decorators import employee_required

customer_bp = Blueprint('customers', __name__, url_prefix='/api/customers')


@customer_bp.route('', methods=['GET'])
@employee_required()
def get_customers():
    """List customer profiles with search and spend metrics."""
    query = Customer.query

    search = request.args.get('search', '').strip()
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Customer.full_name.ilike(search_filter)) |
            (Customer.phone.ilike(search_filter)) |
            (Customer.city.ilike(search_filter))
        )

    sort_by = request.args.get('sort', 'spent_desc')
    if sort_by == 'spent_desc':
        query = query.order_by(Customer.total_spent.desc())
    elif sort_by == 'orders_desc':
        query = query.order_by(Customer.total_orders.desc())
    else:
        query = query.order_by(Customer.id.desc())

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'customers': [c.to_dict() for c in pagination.items]
    }), 200


@customer_bp.route('/<int:customer_id>', methods=['GET'])
@employee_required()
def get_customer(customer_id):
    """Retrieve single customer profile."""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({'success': True, 'customer': customer.to_dict()}), 200


@customer_bp.route('/<int:customer_id>/history', methods=['GET'])
@employee_required()
def get_customer_history(customer_id):
    """Retrieve purchase history for a customer."""
    customer = Customer.query.get_or_404(customer_id)
    orders = customer.orders.order_by(Customer.orders.property.mapper.class_.created_at.desc()).limit(20).all()
    transactions = customer.transactions.order_by(Customer.transactions.property.mapper.class_.created_at.desc()).limit(20).all()

    return jsonify({
        'success': True,
        'customer': customer.to_dict(),
        'orders': [o.to_dict(include_items=True) for o in orders],
        'transactions': [t.to_dict() for t in transactions]
    }), 200
