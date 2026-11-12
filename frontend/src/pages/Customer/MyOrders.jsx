import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Package, Clock, AlertCircle, CheckCircle2, XCircle, ArrowRight } from 'lucide-react';
import api from '../../services/api';

export default function MyOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);

  const fetchOrders = () => {
    setLoading(true);
    api.get('/orders')
      .then((res) => {
        if (res.data.success) {
          setOrders(res.data.orders);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order? Stock will be returned to inventory.')) return;
    setCancellingId(orderId);
    try {
      const res = await api.put(`/orders/${orderId}/cancel`);
      if (res.data.success) {
        alert('Order cancelled successfully.');
        fetchOrders();
      }
    } catch (err) {
      alert(err.response?.data?.error || 'Cancellation failed.');
    } finally {
      setCancellingId(null);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
      case 'DELIVERED':
        return <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" />{status}</span>;
      case 'CANCELLED':
        return <span className="px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-semibold flex items-center gap-1"><XCircle className="w-3.5 h-3.5" />CANCELLED</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-semibold flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{status}</span>;
    }
  };

  if (loading) {
    return <div className="py-20 text-center text-slate-500 font-mono text-sm">Loading order history...</div>;
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">My Order History</h1>
        <p className="text-xs text-slate-400 mt-1">Review your online e-commerce transactions and tracking statuses</p>
      </div>

      {orders.length === 0 ? (
        <div className="py-20 text-center rounded-3xl bg-slate-900 border border-slate-800">
          <Package className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-white">No Orders Placed Yet</h3>
          <p className="text-xs text-slate-400 mt-1 mb-6">Discover products and place your first online simulated order!</p>
          <Link
            to="/products"
            className="py-2.5 px-5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold inline-flex items-center gap-1.5 transition"
          >
            <span>Start Shopping</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((ord) => (
            <div
              key={ord.id}
              className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-lg space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center font-bold">
                    <Package className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="font-mono font-bold text-sm text-white block">#{ord.order_number}</span>
                    <span className="text-[11px] text-slate-400">{ord.created_at ? new Date(ord.created_at).toLocaleString() : 'N/A'}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  {getStatusBadge(ord.order_status)}
                  <span className="text-base font-extrabold text-white font-mono">₹{ord.total_amount}</span>
                </div>
              </div>

              {/* Items List */}
              <div className="divide-y divide-slate-800/60 text-xs">
                {ord.items?.map((item, idx) => (
                  <div key={idx} className="py-2.5 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="w-6 h-6 rounded-lg bg-slate-950 text-slate-400 font-mono flex items-center justify-center text-[10px]">
                        x{item.quantity}
                      </span>
                      <span className="font-medium text-slate-200">{item.product_name}</span>
                    </div>
                    <span className="font-mono text-slate-300">₹{item.subtotal}</span>
                  </div>
                ))}
              </div>

              {/* Order Footer & Cancellation */}
              <div className="pt-3 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
                <span>Store Hub: {ord.store_name || 'Central E-Commerce Hub'}</span>
                {ord.order_status !== 'CANCELLED' && (
                  <button
                    disabled={cancellingId === ord.id}
                    onClick={() => handleCancelOrder(ord.id)}
                    className="text-rose-400 hover:text-rose-300 font-medium transition"
                  >
                    {cancellingId === ord.id ? 'Processing...' : 'Cancel Order & Refund Stock'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
