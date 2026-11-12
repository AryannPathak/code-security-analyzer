"""Physical Store and Centralized Inventory models for SmartFlow."""
from datetime import datetime, timezone
from backend.app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Store(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(60), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    employees = db.relationship('Employee', backref='store', lazy='dynamic')
    inventory_items = db.relationship('Inventory', backref='store', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='store', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='store', lazy='dynamic')
    stock_histories = db.relationship('StockHistory', backref='store', lazy='dynamic')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'store_code': self.store_code,
            'name': self.name,
            'location': self.location,
            'city': self.city,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    safety_stock_level = db.Column(db.Integer, nullable=False, default=15)
    reorder_quantity = db.Column(db.Integer, nullable=False, default=60)
    last_restocked_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    __table_args__ = (
        db.UniqueConstraint('store_id', 'product_id', name='uq_store_product'),
    )

    @property
    def is_low_stock(self) -> bool:
        return self.stock_quantity <= self.safety_stock_level

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'store_id': self.store_id,
            'store_name': self.store.name if self.store else None,
            'product_id': self.product_id,
            'product_sku': self.product.sku if self.product else None,
            'product_name': self.product.name if self.product else None,
            'category_name': self.product.category.name if self.product and self.product.category else None,
            'stock_quantity': self.stock_quantity,
            'safety_stock_level': self.safety_stock_level,
            'reorder_quantity': self.reorder_quantity,
            'is_low_stock': self.is_low_stock,
            'unit_price': float(self.product.price) if self.product else 0.0,
            'last_restocked_at': self.last_restocked_at.isoformat() if self.last_restocked_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StockHistory(db.Model):
    __tablename__ = 'stock_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id', ondelete='RESTRICT'), nullable=False, index=True)
    change_type = db.Column(db.String(30), nullable=False)  # RESTOCK, ONLINE_SALE, STORE_SALE, RETURN, DAMAGE_ADJUSTMENT
    quantity_changed = db.Column(db.Integer, nullable=False)  # Positive for additions, negative for reductions
    balance_after = db.Column(db.Integer, nullable=False)
    reference_id = db.Column(db.String(60), nullable=True)  # Order number, Restock Invoice, etc.
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'store_id': self.store_id,
            'store_name': self.store.name if self.store else None,
            'change_type': self.change_type,
            'quantity_changed': self.quantity_changed,
            'balance_after': self.balance_after,
            'reference_id': self.reference_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
