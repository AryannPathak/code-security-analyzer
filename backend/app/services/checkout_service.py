"""Centralized Omnichannel Checkout & Settlement Service for SmartFlow.
Handles both DMart POS store billing and Amazon-style digital checkout with
strict concurrency row-locking and idempotency key safety.
"""
import uuid
import random
from datetime import datetime, timezone
from backend.app.extensions import db
from backend.app.models.order import Order, OrderItem, Transaction, PaymentRecord
from backend.app.models.store_inventory import Inventory, Store, StockHistory
from backend.app.models.catalog import Product
from backend.app.models.user import Customer
from backend.app.models.cart import Coupon, Cart, CartItem


def generate_order_number(prefix: str = "ORD") -> str:
    """Generate unique order identifier: ORD-YYYYMMDD-XXXX."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_hex = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{date_str}-{random_hex}"


def generate_transaction_id(prefix: str = "TXN") -> str:
    """Generate unique transaction identifier: TXN-YYYYMMDD-XXXX."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_hex = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{date_str}-{random_hex}"


def process_checkout(
    order_type: str,            # 'ONLINE' or 'STORE'
    store_id: int,
    items: list[dict],          # [{'product_id': int, 'quantity': int}]
    payment_method: str,        # 'CASH', 'UPI', 'CARD', 'ONLINE_NETBANKING'
    customer_id: int = None,
    employee_id: int = None,
    coupon_code: str = None,
    shipping_address: str = None,
    idempotency_key: str = None
) -> tuple[bool, dict]:
    """Execute atomic transaction for order and stock deduction.
    Returns: (success: bool, response_data: dict)
    """
    if not items:
        return False, {'error': 'Order must contain at least one item.'}

    # 1. Idempotency Check: Prevent duplicate billing
    if idempotency_key:
        existing_order = Order.query.filter_by(idempotency_key=idempotency_key).first()
        if existing_order:
            return True, {
                'message': 'Order already processed (Idempotent response)',
                'order': existing_order.to_dict(include_items=True),
                'transaction_id': existing_order.transactions[0].transaction_id if existing_order.transactions.count() > 0 else None
            }

    # Verify Store
    store = Store.query.get(store_id)
    if not store or not store.is_active:
        return False, {'error': f'Store ID {store_id} is inactive or not found.'}

    subtotal = 0.0
    processed_items = []

    # 2. Concurrency Safety: Row-Level Locking via with_for_update()
    # Lock and verify inventory balances before deducting
    try:
        for item_data in items:
            product_id = item_data.get('product_id')
            req_qty = int(item_data.get('quantity', 1))

            if req_qty <= 0:
                return False, {'error': f'Invalid quantity {req_qty} for item.'}

            product = Product.query.get(product_id)
            if not product or not product.is_available:
                return False, {'error': f'Product ID {product_id} is unavailable.'}

            # Acquire row lock on the store inventory record
            inv_record = Inventory.query.filter_by(
                store_id=store_id, product_id=product_id
            ).with_for_update().first()

            # If inventory row doesn't exist for store, create with 0 stock
            if not inv_record:
                inv_record = Inventory(store_id=store_id, product_id=product_id, stock_quantity=0)
                db.session.add(inv_record)
                db.session.flush()

            if inv_record.stock_quantity < req_qty:
                db.session.rollback()
                return False, {
                    'error': f'Insufficient stock for "{product.name}". Available: {inv_record.stock_quantity}, Requested: {req_qty}'
                }

            item_subtotal = float(product.price) * req_qty
            subtotal += item_subtotal

            processed_items.append({
                'product': product,
                'inventory_record': inv_record,
                'quantity': req_qty,
                'unit_price': float(product.price),
                'subtotal': item_subtotal
            })

        # 3. Calculate Discount & Taxes
        discount_amount = 0.0
        applied_coupon = None
        if coupon_code:
            coupon = Coupon.query.filter_by(code=coupon_code.strip().upper()).first()
            if coupon:
                is_valid, _ = coupon.is_valid(subtotal)
                if is_valid:
                    discount_amount = coupon.calculate_discount(subtotal)
                    coupon.used_count += 1
                    applied_coupon = coupon

        taxable_amount = max(subtotal - discount_amount, 0.0)
        tax_amount = round(taxable_amount * 0.05, 2)  # Standard 5% GST
        final_total = round(taxable_amount + tax_amount, 2)

        # 4. Create Order Record
        order_number = generate_order_number("ORD" if order_type == "ONLINE" else "POS")
        initial_status = 'CONFIRMED' if order_type == 'ONLINE' else 'COMPLETED'
        order = Order(
            order_number=order_number,
            customer_id=customer_id,
            store_id=store_id,
            employee_id=employee_id,
            order_type=order_type,
            order_status=initial_status,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total_amount=final_total,
            shipping_address=shipping_address,
            idempotency_key=idempotency_key
        )
        db.session.add(order)
        db.session.flush()

        # 5. Decrement Stock & Create Order Items and Stock History
        change_type = 'ONLINE_SALE' if order_type == 'ONLINE' else 'STORE_SALE'
        for p_item in processed_items:
            product = p_item['product']
            inv_record = p_item['inventory_record']
            qty = p_item['quantity']

            # Stock deduction
            inv_record.stock_quantity -= qty

            # Line item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                unit_price=p_item['unit_price'],
                subtotal=p_item['subtotal']
            )
            db.session.add(order_item)

            # Stock Audit Trail
            stock_hist = StockHistory(
                product_id=product.id,
                store_id=store_id,
                change_type=change_type,
                quantity_changed=-qty,
                balance_after=inv_record.stock_quantity,
                reference_id=order.order_number,
                notes=f"{order_type} purchase settlement"
            )
            db.session.add(stock_hist)

        # 6. Centralized Financial Transaction Ledger
        txn_id = generate_transaction_id("TXN")
        transaction = Transaction(
            transaction_id=txn_id,
            order_id=order.id,
            customer_id=customer_id,
            store_id=store_id,
            source=order_type,
            amount=final_total,
            status='SUCCESS',
            payment_method=payment_method,
            is_flagged_anomaly=False,
            anomaly_score=0.0
        )
        db.session.add(transaction)
        db.session.flush()

        # 7. Simulated Payment Record
        gateway_ref = f"SIM-PAY-{uuid.uuid4().hex[:10].upper()}"
        payment_record = PaymentRecord(
            transaction_id=transaction.id,
            payment_gateway_ref=gateway_ref,
            payment_method=payment_method,
            amount=final_total,
            status='SUCCESS',
            response_message=f'Tender {payment_method} approved via simulated gateway.'
        )
        db.session.add(payment_record)

        # 8. Update Customer Profile Metrics
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer:
                customer.total_orders += 1
                customer.total_spent = float(customer.total_spent) + final_total

        # 9. Clear customer online cart if online checkout
        if order_type == 'ONLINE' and customer_id:
            cart = Cart.query.filter_by(customer_id=customer_id).first()
            if cart:
                CartItem.query.filter_by(cart_id=cart.id).delete()

        db.session.commit()

        return True, {
            'message': 'Order and transaction processed successfully.',
            'order': order.to_dict(include_items=True),
            'transaction': transaction.to_dict(),
            'payment_reference': gateway_ref,
            'receipt': {
                'bill_number': order.order_number,
                'store_name': store.name,
                'store_location': f"{store.location}, {store.city}",
                'date': order.created_at.strftime("%d-%b-%Y %I:%M %p"),
                'items_count': len(processed_items),
                'subtotal': subtotal,
                'discount': discount_amount,
                'tax_5pct': tax_amount,
                'final_total': final_total,
                'payment_method': payment_method,
                'payment_ref': gateway_ref
            }
        }

    except Exception as e:
        db.session.rollback()
        return False, {'error': f'Checkout failed due to transactional error: {str(e)}'}
