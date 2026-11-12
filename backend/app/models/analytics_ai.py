"""Recommendation and AuditLog models for SmartFlow."""
from datetime import datetime, timezone
from backend.app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    score = db.Column(db.Numeric(6, 4), nullable=False, default=0.0000)
    strategy = db.Column(db.String(50), nullable=False, default='POPULARITY', index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'score': float(self.score),
            'strategy': self.strategy,
            'is_active': self.is_active,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)  # LOGIN, PRODUCT_CREATE, STOCK_UPDATE, etc.
    entity_type = db.Column(db.String(50), nullable=True)  # PRODUCT, ORDER, INVENTORY, USER
    entity_id = db.Column(db.String(50), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'System',
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'ip_address': self.ip_address,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
