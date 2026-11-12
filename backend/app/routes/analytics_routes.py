"""Enterprise Business Analytics & Dashboard Aggregation routes for SmartFlow."""
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy import func, case
from backend.app.extensions import db
from backend.app.models.order import Order, OrderItem, Transaction
from backend.app.models.catalog import Product, Category
from backend.app.models.user import Customer
from backend.app.models.store_inventory import Inventory, Store
from backend.app.auth.decorators import employee_required, admin_required

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/dashboard', methods=['GET'])
@employee_required()
def get_dashboard_metrics():
    """Real-time enterprise dashboard metrics computed dynamically from database."""
    # 1. High-level KPI aggregations
    total_rev = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.status == 'SUCCESS'
    ).scalar() or 0.0

    total_txns = Transaction.query.count()
    total_orders = Order.query.count()
    total_customers = Customer.query.count()
    total_products = Product.query.count()

    # Order status breakdown
    pending_orders = Order.query.filter(Order.order_status.in_(['PENDING', 'PROCESSING', 'CONFIRMED'])).count()
    completed_orders = Order.query.filter(Order.order_status.in_(['COMPLETED', 'DELIVERED'])).count()
    cancelled_orders = Order.query.filter(Order.order_status == 'CANCELLED').count()

    # Low-stock items
    low_stock_count = Inventory.query.filter(
        Inventory.stock_quantity <= Inventory.safety_stock_level
    ).count()

    # Online vs Offline sales split
    online_rev = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.status == 'SUCCESS', Transaction.source == 'ONLINE'
    ).scalar() or 0.0

    store_rev = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.status == 'SUCCESS', Transaction.source == 'STORE'
    ).scalar() or 0.0

    online_txns = Transaction.query.filter(Transaction.source == 'ONLINE').count()
    store_txns = Transaction.query.filter(Transaction.source == 'STORE').count()

    # 2. Daily Sales Trend (Last 14 days)
    # Using SQL date aggregation for accuracy across both MySQL and SQLite
    daily_sales = []
    now = datetime.now(timezone.utc)
    for i in range(13, -1, -1):
        target_date = (now - timedelta(days=i)).date()
        next_date = target_date + timedelta(days=1)

        day_total = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.status == 'SUCCESS',
            Transaction.created_at >= datetime(target_date.year, target_date.month, target_date.day),
            Transaction.created_at < datetime(next_date.year, next_date.month, next_date.day)
        ).scalar() or 0.0

        daily_sales.append({
            'date': target_date.strftime("%d %b"),
            'full_date': target_date.strftime("%Y-%m-%d"),
            'amount': round(float(day_total), 2)
        })

    # 3. Top Selling Products
    top_products_query = db.session.query(
        Product.id,
        Product.name,
        Product.sku,
        Category.name.label('category_name'),
        func.sum(OrderItem.quantity).label('units_sold'),
        func.sum(OrderItem.subtotal).label('revenue_generated')
    ).join(OrderItem, Product.id == OrderItem.product_id)\
     .join(Category, Product.category_id == Category.id)\
     .group_by(Product.id)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .limit(6).all()

    top_products = [
        {
            'product_id': row[0],
            'name': row[1],
            'sku': row[2],
            'category': row[3],
            'units_sold': int(row[4] or 0),
            'revenue': round(float(row[5] or 0.0), 2)
        }
        for row in top_products_query
    ]

    # 4. Category Performance Breakdown
    cat_perf_query = db.session.query(
        Category.name,
        func.count(Product.id).label('product_count'),
        func.coalesce(func.sum(OrderItem.subtotal), 0.0).label('total_sales')
    ).outerjoin(Product, Category.id == Product.category_id)\
     .outerjoin(OrderItem, Product.id == OrderItem.product_id)\
     .group_by(Category.id)\
     .order_by(func.coalesce(func.sum(OrderItem.subtotal), 0.0).desc()).all()

    category_performance = [
        {
            'category': row[0],
            'product_count': int(row[1] or 0),
            'total_sales': round(float(row[2] or 0.0), 2)
        }
        for row in cat_perf_query
    ]

    # 5. Recent 8 transactions & orders
    recent_txns = Transaction.query.order_by(Transaction.created_at.desc()).limit(8).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    return jsonify({
        'success': True,
        'kpis': {
            'total_revenue': round(float(total_rev), 2),
            'total_transactions': total_txns,
            'total_orders': total_orders,
            'total_customers': total_customers,
            'total_products': total_products,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'low_stock_count': low_stock_count,
            'online_sales': round(float(online_rev), 2),
            'store_sales': round(float(store_rev), 2),
            'online_transactions': online_txns,
            'store_transactions': store_txns
        },
        'daily_sales': daily_sales,
        'top_products': top_products,
        'category_performance': category_performance,
        'recent_transactions': [t.to_dict() for t in recent_txns],
        'recent_orders': [o.to_dict(include_items=False) for o in recent_orders]
    }), 200
