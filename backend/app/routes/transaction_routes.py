"""Unified Centralized Transaction Ledger routes for SmartFlow."""
import csv
import io
from flask import Blueprint, request, jsonify, Response
from backend.app.extensions import db
from backend.app.models.order import Transaction, PaymentRecord
from backend.app.auth.decorators import employee_required, admin_required

transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')


@transaction_bp.route('', methods=['GET'])
@employee_required()
def get_transactions():
    """List unified financial transactions across DMart POS and Amazon online."""
    query = Transaction.query

    source = request.args.get('source')  # ONLINE or STORE
    if source:
        query = query.filter(Transaction.source == source.upper())

    status = request.args.get('status')
    if status:
        query = query.filter(Transaction.status == status.upper())

    payment_method = request.args.get('payment_method')
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method.upper())

    store_id = request.args.get('store_id', type=int)
    if store_id:
        query = query.filter(Transaction.store_id == store_id)

    flagged_only = request.args.get('anomalies_only', 'false').lower() == 'true'
    if flagged_only:
        query = query.filter(Transaction.is_flagged_anomaly == True)

    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(Transaction.transaction_id.ilike(f"%{search}%"))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    pagination = query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'transactions': [t.to_dict() for t in pagination.items]
    }), 200


@transaction_bp.route('/<int:transaction_id>', methods=['GET'])
@employee_required()
def get_transaction(transaction_id):
    """Retrieve single transaction with payment gateway tender responses."""
    txn = Transaction.query.get_or_404(transaction_id)
    data = txn.to_dict()
    data['payment_records'] = [pr.to_dict() for pr in txn.payment_records]
    return jsonify({'success': True, 'transaction': data}), 200


@transaction_bp.route('/<int:transaction_id>/anomaly-status', methods=['PUT'])
@admin_required()
def update_anomaly_status(transaction_id):
    """Admin review of flagged unusual transaction."""
    txn = Transaction.query.get_or_404(transaction_id)
    data = request.get_json() or {}
    is_flagged = bool(data.get('is_flagged_anomaly', False))

    txn.is_flagged_anomaly = is_flagged
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Anomaly flag updated to {is_flagged}",
        'transaction': txn.to_dict()
    }), 200


@transaction_bp.route('/export', methods=['GET'])
@admin_required()
def export_transactions_csv():
    """Export transactions to a downloadable CSV file."""
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Transaction ID', 'Order Number', 'Source', 'Store', 'Customer',
        'Amount (INR)', 'Payment Method', 'Status', 'Is Anomaly', 'Anomaly Score', 'Date'
    ])

    for t in transactions:
        writer.writerow([
            t.transaction_id,
            t.order.order_number if t.order else 'N/A',
            t.source,
            t.store.name if t.store else 'N/A',
            t.customer.full_name if t.customer else 'Store Walk-in',
            float(t.amount),
            t.payment_method,
            t.status,
            'YES' if t.is_flagged_anomaly else 'NO',
            round(t.anomaly_score, 4),
            t.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=smartflow_transactions.csv"}
    )
