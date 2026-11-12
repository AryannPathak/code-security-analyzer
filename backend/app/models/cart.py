"""Shopping Cart, CartItem, and Coupon models for SmartFlow."""
from datetime import datetime, timezone
from backend.app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy='joined', cascade='all, delete-orphan')

    @property
    def total_amount(self) -> float:
        return sum(item.quantity * float(item.product.price) for item in self.items if item.product)

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    def to_dict(self) -> dict:
        cart_items_data = [item.to_dict() for item in self.items]
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'items': cart_items_data,
            'total_items': self.total_items,
            'total_amount': round(self.total_amount, 2),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    __table_args__ = (
        db.UniqueConstraint('cart_id', 'product_id', name='uq_cart_product'),
    )

    def to_dict(self) -> dict:
        unit_price = float(self.product.price) if self.product else 0.0
        mrp = float(self.product.mrp) if self.product else 0.0
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_sku': self.product.sku if self.product else None,
            'product_image': self.product.image_url if self.product else None,
            'unit': self.product.unit if self.product else 'piece',
            'unit_price': unit_price,
            'mrp': mrp,
            'quantity': self.quantity,
            'subtotal': round(self.quantity * unit_price, 2)
        }


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    discount_percent = db.Column(db.Numeric(5, 2), nullable=False)
    max_discount_amount = db.Column(db.Numeric(10, 2), nullable=True)
    min_order_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    usage_limit = db.Column(db.Integer, nullable=False, default=1000)
    used_count = db.Column(db.Integer, nullable=False, default=0)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    def is_valid(self, order_amount: float) -> tuple[bool, str]:
        """Validate if coupon can be applied to given amount."""
        if not self.is_active:
            return False, 'Coupon is inactive or disabled'
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires:
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if now > expires:
                return False, 'Coupon has expired'
        if self.used_count >= self.usage_limit:
            return False, 'Coupon usage limit has been reached'
        if order_amount < float(self.min_order_amount):
            return False, f'Minimum order amount of ₹{float(self.min_order_amount):.2f} required'
        return True, 'Coupon is valid'

    def calculate_discount(self, order_amount: float) -> float:
        """Calculate discount value based on percent and cap."""
        discount = (order_amount * float(self.discount_percent)) / 100.0
        if self.max_discount_amount and discount > float(self.max_discount_amount):
            discount = float(self.max_discount_amount)
        return round(discount, 2)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'code': self.code,
            'discount_percent': float(self.discount_percent),
            'max_discount_amount': float(self.max_discount_amount) if self.max_discount_amount else None,
            'min_order_amount': float(self.min_order_amount),
            'usage_limit': self.usage_limit,
            'used_count': self.used_count,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
