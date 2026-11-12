"""Central model index for SmartFlow.
Exports all 18 database entities.
"""
from backend.app.extensions import db

# Core Authentication & Participants
from backend.app.models.user import User, Customer, Employee

# Product Catalog
from backend.app.models.catalog import Category, Product

# Stores & Centralized Inventory
from backend.app.models.store_inventory import Store, Inventory, StockHistory

# Orders, Transactions & Settlements
from backend.app.models.order import Order, OrderItem, Transaction, PaymentRecord, Return

# Customer Shopping Cart & Loyalty
from backend.app.models.cart import Cart, CartItem, Coupon

# AI Recommendations & Security Auditing
from backend.app.models.analytics_ai import Recommendation, AuditLog

__all__ = [
    'db',
    'User',
    'Customer',
    'Employee',
    'Category',
    'Product',
    'Store',
    'Inventory',
    'StockHistory',
    'Order',
    'OrderItem',
    'Transaction',
    'PaymentRecord',
    'Return',
    'Cart',
    'CartItem',
    'Coupon',
    'Recommendation',
    'AuditLog',
]
