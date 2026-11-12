"""Unified Order, OrderItem, Transaction, Payment and Return models for SmartFlow."""
from datetime import datetime, timezone
from backend.app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id', ondelete='RESTRICT'), nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='SET NULL'), nullable=True)
    order_type = db.Column(db.String(20), nullable=False, index=True)  # ONLINE, STORE
    order_status = db.Column(
        db.String(30), nullable=False, default='COMPLETED', index=True
    )  # PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, COMPLETED, CANCELLED
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    discount_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    tax_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    shipping_address = db.Column(db.Text, nullable=True)
    idempotency_key = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='joined', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='order', lazy='dynamic')
    returns = db.relationship('Return', backref='order', lazy='dynamic')

    def to_dict(self, include_items: bool = True) -> dict:
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else 'Guest / Walk-in Customer',
            'customer_email': self.customer.user.email if (self.customer and self.customer.user) else None,
            'store_id': self.store_id,
            'store_name': self.store.name if self.store else None,
            'employee_id': self.employee_id,
            'employee_name': self.processed_by_employee.full_name if self.processed_by_employee else None,
            'order_type': self.order_type,
            'order_status': self.order_status,
            'subtotal': float(self.subtotal),
            'discount_amount': float(self.discount_amount),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'shipping_address': self.shipping_address,
            'idempotency_key': self.idempotency_key,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
            data['total_items_count'] = sum(item.quantity for item in self.items)
        return data


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_sku': self.product.sku if self.product else None,
            'product_name': self.product.name if self.product else None,
            'product_image': self.product.image_url if self.product else None,
            'unit': self.product.unit if self.product else 'piece',
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal)
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.String(60), unique=True, nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='RESTRICT'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id', ondelete='RESTRICT'), nullable=False, index=True)
    source = db.Column(db.String(20), nullable=False)  # ONLINE, STORE
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='SUCCESS', index=True)  # SUCCESS, FAILED, REFUNDED, PENDING
    payment_method = db.Column(db.String(30), nullable=False)  # CASH, UPI, CARD, ONLINE_NETBANKING
    is_flagged_anomaly = db.Column(db.Boolean, nullable=False, default=False, index=True)
    anomaly_score = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    payment_records = db.relationship('PaymentRecord', backref='transaction', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'order_id': self.order_id,
            'order_number': self.order.order_number if self.order else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else 'Guest / Store Walk-in',
            'store_id': self.store_id,
            'store_name': self.store.name if self.store else None,
            'source': self.source,
            'amount': float(self.amount),
            'status': self.status,
            'payment_method': self.payment_method,
            'is_flagged_anomaly': self.is_flagged_anomaly,
            'anomaly_score': round(float(self.anomaly_score), 4),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PaymentRecord(db.Model):
    __tablename__ = 'payment_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False, index=True)
    payment_gateway_ref = db.Column(db.String(100), nullable=True, index=True)
    payment_method = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # SUCCESS, FAILED, REFUNDED
    response_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'payment_gateway_ref': self.payment_gateway_ref,
            'payment_method': self.payment_method,
            'amount': float(self.amount),
            'status': self.status,
            'response_message': self.response_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Return(db.Model):
    __tablename__ = 'returns'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    refund_amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, APPROVED, REJECTED, COMPLETED
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationship to product
    product = db.relationship('Product', backref='returns')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'refund_amount': float(self.refund_amount),
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
