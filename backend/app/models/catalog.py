"""Product and Category models for SmartFlow."""
from datetime import datetime, timezone
from backend.app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'products_count': self.products.count() if hasattr(self, 'products') else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(60), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(20), nullable=False, default='piece')  # piece, kg, litre, pack
    mrp = db.Column(db.Numeric(10, 2), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    inventory_items = db.relationship('Inventory', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    stock_histories = db.relationship('StockHistory', backref='product', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic')
    recommendation = db.relationship('Recommendation', backref='product', uselist=False, cascade='all, delete-orphan')

    @property
    def total_stock(self) -> int:
        """Sum stock across all physical stores and fulfillment hubs."""
        total = db.session.query(db.func.sum(Inventory.stock_quantity)).filter(
            Inventory.product_id == self.id
        ).scalar()
        return int(total) if total else 0

    def to_dict(self, include_inventory: bool = False) -> dict:
        discount_pct = 0.0
        if self.mrp and float(self.mrp) > float(self.price):
            discount_pct = round(((float(self.mrp) - float(self.price)) / float(self.mrp)) * 100, 1)

        data = {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'sku': self.sku,
            'barcode': self.barcode,
            'name': self.name,
            'description': self.description,
            'brand': self.brand,
            'unit': self.unit,
            'mrp': float(self.mrp),
            'price': float(self.price),
            'cost_price': float(self.cost_price),
            'discount_percent': discount_pct,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_inventory:
            store_stocks = [
                {
                    'store_id': inv.store_id,
                    'store_name': inv.store.name if inv.store else None,
                    'stock_quantity': inv.stock_quantity,
                    'safety_stock_level': inv.safety_stock_level,
                    'is_low_stock': inv.stock_quantity <= inv.safety_stock_level
                }
                for inv in self.inventory_items
            ]
            data['inventory'] = store_stocks
            data['total_stock'] = sum(s['stock_quantity'] for s in store_stocks)
        return data


# Imported inside property to avoid circular imports
from backend.app.models.store_inventory import Inventory  # noqa: E402
