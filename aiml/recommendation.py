"""FEATURE 2: POPULARITY-BASED PRODUCT RECOMMENDATION
SmartFlow AIML Module - 3rd Year AIML Major Project

Algorithm: Popularity-Based & Frequency Ranking
Objective: Recommend trending, top-selling products to customers on homepage & catalog.
"""
from typing import List, Dict, Optional
from backend.app.extensions import db
from backend.app.models.catalog import Product, Category
from backend.app.models.order import OrderItem


class ProductRecommender:
    def __init__(self):
        pass

    def get_popular_recommendations(
        self,
        category_id: Optional[int] = None,
        limit: int = 8,
        exclude_product_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """Rank and return top products based on verified purchase volume in order_items."""
        query = db.session.query(
            Product,
            db.func.coalesce(db.func.sum(OrderItem.quantity), 0).label('total_purchases')
        ).outerjoin(OrderItem, Product.id == OrderItem.product_id)\
         .filter(Product.is_available == True)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if exclude_product_ids:
            query = query.filter(~Product.id.in_(exclude_product_ids))

        results = query.group_by(Product.id)\
                       .order_by(db.func.coalesce(db.func.sum(OrderItem.quantity), 0).desc())\
                       .limit(limit)\
                       .all()

        recommendations = []
        max_purchases = max([row[1] for row in results], default=1) or 1

        for product, purchases in results:
            # Normalized popularity score (0.00 to 1.00)
            score = round(purchases / max_purchases, 4) if max_purchases > 0 else 0.5
            p_data = product.to_dict(include_inventory=False)
            p_data['popularity_score'] = score
            p_data['total_units_sold'] = int(purchases)
            p_data['recommendation_reason'] = f"Top trending item with {purchases} customer purchases"
            recommendations.append(p_data)

        # Fallback if catalog has zero sales yet: return first available products
        if not recommendations:
            fallback_products = Product.query.filter_by(is_available=True).limit(limit).all()
            for p in fallback_products:
                p_data = p.to_dict(include_inventory=False)
                p_data['popularity_score'] = 0.50
                p_data['total_units_sold'] = 0
                p_data['recommendation_reason'] = "Featured staple item"
                recommendations.append(p_data)

        return recommendations
