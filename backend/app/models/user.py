"""User, Customer and Employee models for SmartFlow."""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from backend.app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(60), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='CUSTOMER', index=True)  # ADMIN, CUSTOMER, EMPLOYEE
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    customer_profile = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    employee_profile = db.relationship('Employee', backref='user', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password: str):
        """Hash and store the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the plain-text password against the hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive: bool = False) -> dict:
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if self.customer_profile:
            data['customer_profile'] = {
                'id': self.customer_profile.id,
                'full_name': self.customer_profile.full_name,
                'phone': self.customer_profile.phone,
                'city': self.customer_profile.city,
                'total_orders': self.customer_profile.total_orders,
                'total_spent': float(self.customer_profile.total_spent)
            }
        if self.employee_profile:
            data['employee_profile'] = {
                'id': self.employee_profile.id,
                'employee_code': self.employee_profile.employee_code,
                'full_name': self.employee_profile.full_name,
                'position': self.employee_profile.position,
                'shift': self.employee_profile.shift,
                'store_id': self.employee_profile.store_id
            }
        return data


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True, index=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(60), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    total_orders = db.Column(db.Integer, nullable=False, default=0)
    total_spent = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='customer', lazy='dynamic')
    cart = db.relationship('Cart', backref='customer', uselist=False, cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'email': self.user.email if self.user else None,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'total_orders': self.total_orders,
            'total_spent': float(self.total_spent),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id', ondelete='SET NULL'), nullable=True, index=True)
    employee_code = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(60), nullable=False, default='Cashier')  # Cashier, Store Manager, Inventory Clerk
    shift = db.Column(db.String(20), nullable=False, default='GENERAL')     # MORNING, EVENING, NIGHT, GENERAL
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    orders_processed = db.relationship('Order', backref='processed_by_employee', lazy='dynamic')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'email': self.user.email if self.user else None,
            'store_id': self.store_id,
            'store_name': self.store.name if self.store else None,
            'employee_code': self.employee_code,
            'full_name': self.full_name,
            'position': self.position,
            'shift': self.shift,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
