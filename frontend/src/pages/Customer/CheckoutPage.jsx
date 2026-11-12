import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { 
  CreditCard, 
  Smartphone, 
  Building, 
  ShieldCheck, 
  CheckCircle2, 
  ArrowRight, 
  Loader2,
  Package,
  Calendar,
  MapPin,
  Clock
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';

export default function CheckoutPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { cart, refreshCart } = useCart();
  const { user } = useAuth();

  const couponCode = location.state?.couponCode || '';

  const [paymentMethod, setPaymentMethod] = useState('UPI');
  const [shippingAddress, setShippingAddress] = useState(
    user?.customer_profile?.address || 'Flat 402, Green Valley Apartments, Mumbai, Maharashtra'
  );
  const [isProcessing, setIsProcessing] = useState(false);
  const [completedOrder, setCompletedOrder] = useState(null);
  const [error, setError] = useState('');

  // Client-side idempotency key to prevent double checkout clicks
  const [idempotencyKey] = useState(() => 'IDEMP-' + Math.random().toString(36).substring(2, 12).toUpperCase());

  const handleSimulatePayment = async (e) => {
    e.preventDefault();
    setError('');
    setIsProcessing(true);

    try {
      // Small simulated bank delay for realistic UX
      await new Promise((r) => setTimeout(r, 1200));

      const res = await api.post('/orders', {
        payment_method: paymentMethod,
        shipping_address: shippingAddress,
        coupon_code: couponCode || undefined,
        idempotency_key: idempotencyKey,
        store_id: 1 // Central E-commerce Hub
      });

      if (res.data.success) {
        setCompletedOrder(res.data.data.order);
        refreshCart();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Simulated checkout failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (completedOrder) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/10 animate-bounce">
          <CheckCircle2 className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-mono font-semibold">
            Order Confirmed &bull; Payment Successful
          </span>
          <h2 className="text-3xl font-bold text-white tracking-tight">
            Thank You, {user?.username || 'Shopper'}!
          </h2>
          <p className="text-slate-400 text-sm">
            Your simulated order <span className="text-white font-mono font-bold">#{completedOrder.order_number}</span> has been confirmed.
          </p>
        </div>

        {/* Order Tracking Timeline */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 text-left space-y-6 shadow-xl">
          <h3 className="font-bold text-white text-sm pb-3 border-b border-slate-800">Order Delivery Timeline</h3>

          <div className="space-y-6 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-800">
            <div className="flex items-start space-x-4 relative">
              <div className="w-7 h-7 rounded-full bg-emerald-500 text-slate-950 font-bold flex items-center justify-center text-xs shrink-0 ring-4 ring-slate-900">
                ✓
              </div>
              <div>
                <h4 className="text-sm font-semibold text-white">Order Confirmed &amp; Payment Settled</h4>
                <p className="text-xs text-slate-400">Transaction validated &bull; Stock allocated with row lock</p>
              </div>
            </div>

            <div className="flex items-start space-x-4 relative">
              <div className="w-7 h-7 rounded-full bg-blue-500 text-white font-bold flex items-center justify-center text-xs shrink-0 ring-4 ring-slate-900 animate-pulse">
                2
              </div>
              <div>
                <h4 className="text-sm font-semibold text-white">Warehouse Packing in Progress</h4>
                <p className="text-xs text-slate-400">SmartFlow Central Warehouse &amp; E-Commerce Hub (HUB-001)</p>
              </div>
            </div>

            <div className="flex items-start space-x-4 relative">
              <div className="w-7 h-7 rounded-full bg-slate-800 text-slate-500 font-bold flex items-center justify-center text-xs shrink-0 ring-4 ring-slate-900">
                3
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-500">Out for Final Delivery</h4>
                <p className="text-xs text-slate-600">Standard delivery via local courier partner</p>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/80 flex justify-between text-xs text-slate-400 font-mono">
            <span>Total Settled: ₹{completedOrder.total_amount}</span>
            <span>Items: {completedOrder.items?.length || 1} units</span>
          </div>
        </div>

        <div className="flex justify-center space-x-4 pt-4">
          <Link
            to="/orders"
            className="py-3 px-6 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-md transition"
          >
            View in My Orders
          </Link>
          <Link
            to="/products"
            className="py-3 px-6 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition"
          >
            Continue Shopping
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Simulated E-Commerce Checkout</h1>
        <p className="text-xs text-slate-400 mt-1">Safe academic simulation of digital payments &amp; order settlement</p>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-950/60 border border-rose-800/60 text-rose-400 text-xs">
          {error}
        </div>
      )}

      <form onSubmit={handleSimulatePayment} className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6">
          {/* Shipping Address */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center space-x-2 text-white font-bold text-sm">
              <MapPin className="w-4 h-4 text-blue-400" />
              <span>1. Shipping Destination</span>
            </div>
            <textarea
              rows={3}
              value={shippingAddress}
              onChange={(e) => setShippingAddress(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-2xl bg-slate-950 border border-slate-800 focus:border-blue-500 text-sm text-white placeholder-slate-500 transition leading-relaxed"
              placeholder="Enter full street delivery address"
            />
          </div>

          {/* Payment Method Selector */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center space-x-2 text-white font-bold text-sm">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>2. Select Simulated Payment Tender</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <label
                className={`p-4 rounded-2xl border cursor-pointer flex flex-col justify-between transition ${
                  paymentMethod === 'UPI'
                    ? 'bg-blue-950/50 border-blue-500 text-white'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <Smartphone className="w-5 h-5 text-blue-400" />
                  <input
                    type="radio"
                    name="pay"
                    checked={paymentMethod === 'UPI'}
                    onChange={() => setPaymentMethod('UPI')}
                    className="accent-blue-500"
                  />
                </div>
                <div>
                  <span className="font-bold text-xs block text-white">UPI Simulation</span>
                  <span className="text-[10px] text-slate-400">GPay &bull; PhonePe &bull; Paytm</span>
                </div>
              </label>

              <label
                className={`p-4 rounded-2xl border cursor-pointer flex flex-col justify-between transition ${
                  paymentMethod === 'CARD'
                    ? 'bg-blue-950/50 border-blue-500 text-white'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <CreditCard className="w-5 h-5 text-amber-400" />
                  <input
                    type="radio"
                    name="pay"
                    checked={paymentMethod === 'CARD'}
                    onChange={() => setPaymentMethod('CARD')}
                    className="accent-blue-500"
                  />
                </div>
                <div>
                  <span className="font-bold text-xs block text-white">Card Simulation</span>
                  <span className="text-[10px] text-slate-400">Visa &bull; MasterCard &bull; RuPay</span>
                </div>
              </label>

              <label
                className={`p-4 rounded-2xl border cursor-pointer flex flex-col justify-between transition ${
                  paymentMethod === 'ONLINE_NETBANKING'
                    ? 'bg-blue-950/50 border-blue-500 text-white'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <Building className="w-5 h-5 text-emerald-400" />
                  <input
                    type="radio"
                    name="pay"
                    checked={paymentMethod === 'ONLINE_NETBANKING'}
                    onChange={() => setPaymentMethod('ONLINE_NETBANKING')}
                    className="accent-blue-500"
                  />
                </div>
                <div>
                  <span className="font-bold text-xs block text-white">Netbanking</span>
                  <span className="text-[10px] text-slate-400">HDFC &bull; SBI &bull; ICICI</span>
                </div>
              </label>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-[11px] text-slate-400 flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Simulated Payment Gateway: No real financial funds are debited.</span>
            </div>
          </div>
        </div>

        {/* Right Summary Card */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-6 h-fit shadow-xl">
          <h3 className="font-bold text-white text-base pb-3 border-b border-slate-800">Checkout Summary</h3>

          <div className="space-y-3 text-xs text-slate-400">
            <div className="flex justify-between">
              <span>Items Total:</span>
              <span className="text-white font-mono">₹{cart.total_amount.toFixed(2)}</span>
            </div>
            {couponCode && (
              <div className="flex justify-between text-emerald-400">
                <span>Active Coupon:</span>
                <span className="font-mono">{couponCode}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span>Standard GST (5%):</span>
              <span className="text-white font-mono">₹{(cart.total_amount * 0.05).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-base font-bold text-white pt-3 border-t border-slate-800">
              <span>Total Payable:</span>
              <span className="text-amber-400 font-mono">₹{(cart.total_amount * 1.05).toFixed(2)}</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={isProcessing}
            className="w-full py-3.5 px-4 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold text-sm shadow-lg shadow-amber-500/20 flex items-center justify-center space-x-2 transition"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Simulating Gateway Authorization...</span>
              </>
            ) : (
              <>
                <span>Confirm &amp; Place Order</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
