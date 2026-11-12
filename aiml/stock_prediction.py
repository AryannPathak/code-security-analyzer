"""FEATURE 4: INVENTORY DEMAND PREDICTION USING MOVING AVERAGE
SmartFlow AIML Module - 3rd Year AIML Major Project

Algorithm: Moving Average (7-Day & 30-Day Windows)
Objective: Estimate future product demand rates, predict stock exhaustion timelines,
and generate smart replenishment alerts for store managers.
"""
from datetime import datetime, timedelta, timezone
from backend.app.extensions import db
from backend.app.models.store_inventory import Inventory, Store
from backend.app.models.order import OrderItem, Order
from backend.app.models.catalog import Product


class DemandForecaster:
    def __init__(self):
        pass

    def forecast_inventory_demand(self, store_id: int = None, limit: int = 50) -> list[dict]:
        """Compute moving average consumption rates and restock recommendations."""
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        seven_days_ago = now - timedelta(days=7)

        # Retrieve inventory items
        query = Inventory.query
        if store_id:
            query = query.filter(Inventory.store_id == store_id)

        inventory_items = query.limit(limit).all()
        forecast_reports = []

        for inv in inventory_items:
            product = inv.product
            store = inv.store
            if not product or not store:
                continue

            # Units sold in last 30 days
            sales_30d = db.session.query(db.func.sum(OrderItem.quantity))\
                .join(Order, OrderItem.order_id == Order.id)\
                .filter(
                    OrderItem.product_id == product.id,
                    Order.store_id == store.id,
                    Order.created_at >= thirty_days_ago,
                    Order.order_status.in_(['COMPLETED', 'DELIVERED', 'SHIPPED'])
                ).scalar() or 0

            # Units sold in last 7 days
            sales_7d = db.session.query(db.func.sum(OrderItem.quantity))\
                .join(Order, OrderItem.order_id == Order.id)\
                .filter(
                    OrderItem.product_id == product.id,
                    Order.store_id == store.id,
                    Order.created_at >= seven_days_ago,
                    Order.order_status.in_(['COMPLETED', 'DELIVERED', 'SHIPPED'])
                ).scalar() or 0

            # Moving average daily demand
            ma_daily_30d = round(float(sales_30d) / 30.0, 2)
            ma_daily_7d = round(float(sales_7d) / 7.0, 2)

            # Blended demand (weighted towards recent 7 days: 70% 7-day + 30% 30-day)
            daily_demand_rate = round((0.7 * ma_daily_7d) + (0.3 * ma_daily_30d), 2)
            if daily_demand_rate == 0:
                daily_demand_rate = 0.5  # Baseline expectation for active inventory

            # Days of stock remaining
            days_remaining = round(inv.stock_quantity / daily_demand_rate, 1)

            # Priority assignment
            if inv.stock_quantity <= inv.safety_stock_level or days_remaining <= 3:
                priority = 'CRITICAL'
                status_color = 'rose'
            elif days_remaining <= 7:
                priority = 'HIGH'
                status_color = 'amber'
            else:
                priority = 'NORMAL'
                status_color = 'emerald'

            # Recommended reorder units to cover 30 days of safe runway
            target_stock = int(daily_demand_rate * 30) + inv.safety_stock_level
            suggested_reorder = max(target_stock - inv.stock_quantity, 0)

            forecast_reports.append({
                'inventory_id': inv.id,
                'store_id': store.id,
                'store_name': store.name,
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'current_stock': inv.stock_quantity,
                'safety_stock': inv.safety_stock_level,
                'sales_7d': int(sales_7d),
                'sales_30d': int(sales_30d),
                'daily_demand_rate': daily_demand_rate,
                'days_remaining': days_remaining,
                'suggested_reorder': suggested_reorder,
                'priority': priority,
                'status_color': status_color
            })

        # Sort: CRITICAL priority first, then lowest days remaining
        priority_weights = {'CRITICAL': 0, 'HIGH': 1, 'NORMAL': 2}
        forecast_reports.sort(key=lambda x: (priority_weights[x['priority']], x['days_remaining']))

        return forecast_reports
