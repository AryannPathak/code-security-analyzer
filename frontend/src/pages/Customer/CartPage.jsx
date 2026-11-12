import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ShoppingCart, 
  Trash2, 
  Plus, 
  Minus, 
  ArrowRight, 
  Tag, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import api from '../../services/api';

export default function CartPage() {
  const { cart, updateQuantity, removeFromCart, clearCart } = useCart();
  const [couponCode, setCouponCode] = useState('WELCOME50');
  const [discountInfo, setDiscountInfo] = useState(null);
  const [couponError, setCouponError] = useState('');
  const [validatingCoupon, setValidatingCoupon] = useState(false);

  const navigate = useNavigate();

  const handleApplyCoupon = async (e) => {
    e.preventDefault();
    if (!couponCode.trim()) return;

    setValidatingCoupon(true);
    setCouponError('');
    try {
      const res = await api.post('/coupons/validate', {
        code: couponCode.trim(),
        order_amount: cart.total_amount,
      });
      if (res.data.success) {
        setDiscountInfo(res.data.coupon);
      }
    } catch (err) {
      setDiscountInfo(null);
      setCouponError(err.response?.data?.error || 'Invalid or expired coupon code.');
    } finally {
      setValidatingCoupon(false);
    }
  };

  const discountAmount = discountInfo ? discountInfo.discount_amount : 0.0;
  const taxableSubtotal = Math.max(cart.total_amount - discountAmount, 0.0);
  const taxAmount = Number((taxableSubtotal * 0.05).toFixed(2));
  const finalTotal = Number((taxableSubtotal + taxAmount).toFixed(2));

  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto py-20 text-center">
        <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto mb-4 text-slate-500">
          <ShoppingCart className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Your Shopping Cart is Empty</h2>
        <p className="text-slate-400 text-sm mb-6">
          Looks like you haven't added anything to your cart yet. Explore our supermarket catalog!
        </p>
        <Link
          to="/products"
          className="inline-flex items-center space-x-2 py-3 px-6 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-md transition"
        >
          <span>Start Shopping</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Shopping Cart</h1>
        <p className="text-xs text-slate-400 mt-1">Review your selections before simulated checkout</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 text-xs text-slate-400">
            <span>{cart.total_items} items in cart</span>
            <button
              onClick={clearCart}
              className="text-rose-400 hover:text-rose-300 font-medium transition"
            >
              Empty Cart
            </button>
          </div>

          <div className="space-y-3">
            {cart.items.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 rounded-xl overflow-hidden bg-slate-950 shrink-0">
                    <img
                      src={item.product_image || 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80'}
                      alt={item.product_name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white line-clamp-1">{item.product_name}</h4>
                    <span className="text-[11px] font-mono text-slate-400 block">{item.product_sku}</span>
                    <span className="text-xs font-bold text-blue-400 mt-1 block">₹{item.unit_price}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  {/* Quantity Stepper */}
                  <div className="flex items-center space-x-1.5 p-1 rounded-xl bg-slate-950 border border-slate-800">
                    <button
                      onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                      className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                    >
                      <Minus className="w-3.5 h-3.5" />
                    </button>
                    <span className="w-8 text-center text-xs font-bold text-white font-mono">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                      className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                    >
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="w-20 text-right">
                    <span className="text-sm font-bold text-white">₹{item.subtotal}</span>
                  </div>

                  <button
                    onClick={() => removeFromCart(item.product_id)}
                    className="p-2 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-950/40 transition"
                    title="Remove Item"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Order Summary & Coupon Card */}
        <div className="space-y-6">
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
            <h3 className="font-bold text-white text-base pb-3 border-b border-slate-800">Order Summary</h3>

            {/* Coupon Code Input */}
            <form onSubmit={handleApplyCoupon} className="space-y-2">
              <label className="block text-xs font-medium text-slate-300">Promotional Coupon</label>
              <div className="flex space-x-2">
                <div className="relative flex-1">
                  <Tag className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                    placeholder="ENTER CODE"
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-blue-500 text-xs text-white uppercase font-mono tracking-wider transition"
                  />
                </div>
                <button
                  type="submit"
                  disabled={validatingCoupon}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition"
                >
                  Apply
                </button>
              </div>

              {discountInfo && (
                <div className="p-2.5 rounded-xl bg-emerald-950/60 border border-emerald-800/60 flex items-center space-x-2 text-emerald-400 text-xs">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>Coupon {discountInfo.code} applied! Saved ₹{discountInfo.discount_amount}</span>
                </div>
              )}

              {couponError && (
                <div className="p-2.5 rounded-xl bg-rose-950/60 border border-rose-800/60 flex items-center space-x-2 text-rose-400 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{couponError}</span>
                </div>
              )}
            </form>

            {/* Summary Line Items */}
            <div className="space-y-2.5 text-xs text-slate-400 pt-2 border-t border-slate-800">
              <div className="flex justify-between">
                <span>Merchandise Subtotal:</span>
                <span className="font-mono text-white">₹{cart.total_amount.toFixed(2)}</span>
              </div>
              {discountAmount > 0 && (
                <div className="flex justify-between text-emerald-400 font-medium">
                  <span>Coupon Discount ({discountInfo?.discount_percent}%):</span>
                  <span className="font-mono">-₹{discountAmount.toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>GST (5% Standard):</span>
                <span className="font-mono text-white">₹{taxAmount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Delivery Charges:</span>
                <span className="text-emerald-400 font-semibold uppercase">FREE</span>
              </div>
              <div className="flex justify-between text-base font-bold text-white pt-3 border-t border-slate-800">
                <span>Total Amount:</span>
                <span className="text-blue-400 font-mono">₹{finalTotal.toFixed(2)}</span>
              </div>
            </div>

            <button
              onClick={() => navigate('/checkout', { state: { couponCode: discountInfo?.code } })}
              className="w-full py-3.5 px-4 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-sm shadow-lg shadow-amber-500/20 flex items-center justify-center space-x-2 transition"
            >
              <span>Proceed to Simulated Checkout</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <div className="pt-2 flex items-center justify-center space-x-1.5 text-[11px] text-slate-500">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Idempotent Safe Transaction &bull; Row-Lock Protection</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
