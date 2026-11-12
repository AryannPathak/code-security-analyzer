"""Database Connection & Integrity Diagnostic Script for SmartFlow.
Checks connection to MySQL/SQLite and verifies all 18 tables.
"""
import os
import sys

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import inspect
from backend.app import create_app
from backend.app.extensions import db

EXPECTED_TABLES = [
    'users',
    'customers',
    'employees',
    'categories',
    'products',
    'stores',
    'inventory',
    'orders',
    'order_items',
    'transactions',
    'payment_records',
    'cart',
    'cart_items',
    'coupons',
    'stock_history',
    'returns',
    'recommendations',
    'audit_logs'
]

def run_diagnostics():
    print("=" * 65)
    print("    SMARTFLOW DATABASE DIAGNOSTIC & VERIFICATION SUITE")
    print("=" * 65)

    app = create_app()
    with app.app_context():
        engine = db.engine
        print(f"[*] Connected Database Dialect: {engine.name.upper()}")
        print(f"[*] Connection URL: {engine.url}")

        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())

        print(f"[*] Found {len(existing_tables)} existing tables in database:\n")
        all_passed = True
        for idx, table in enumerate(EXPECTED_TABLES, start=1):
            if table in existing_tables:
                columns = inspector.get_columns(table)
                pks = [c['name'] for c in columns if c.get('primary_key')]
                fks = inspector.get_foreign_keys(table)
                print(f"  [{idx:02d}/18]  OK  Table: {table:<18} (Cols: {len(columns):<2}, PK: {','.join(pks)}, FKs: {len(fks)})")
            else:
                print(f"  [{idx:02d}/18] FAIL Table: {table:<18} NOT FOUND!")
                all_passed = False

        print("\n" + "-" * 65)
        if all_passed:
            print(">>> SUCCESS: All 18 SmartFlow database tables verified!")
        else:
            print(">>> WARNING: Some tables are missing. Run `python backend/run.py db-init`")
        print("=" * 65)
        return all_passed

if __name__ == '__main__':
    success = run_diagnostics()
    sys.exit(0 if success else 1)
